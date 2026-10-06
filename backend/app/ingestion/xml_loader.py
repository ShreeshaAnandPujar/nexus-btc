"""Safe XML transaction loader preventing XXE and entity expansion attacks."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Generator, Any
from app.ingestion.normalizer import normalize_raw_record


class XmlLoader:
    """Hardened XML parser designed for security against XXE and entity injection."""

    @staticmethod
    def _sanitize_xml(content: str) -> str:
        # Prevent XML External Entity (XXE) and entity expansion
        if "<!DOCTYPE" in content.upper() or "<!ENTITY" in content.upper():
            raise ValueError("Forbidden XML constructs detected (DOCTYPE or ENTITY not permitted)")
        return content

    @classmethod
    def parse_content(
        cls, content: str | bytes, source_file: str = "upload.xml"
    ) -> Generator[tuple[dict[str, Any], list[str], str, int], None, None]:
        text = content.decode("utf-8", errors="replace") if isinstance(content, bytes) else content
        try:
            clean_text = cls._sanitize_xml(text)
            root = ET.fromstring(clean_text)
        except Exception as e:
            yield {"raw": text[:500], "error": str(e)}, ["FLAG_XML_PARSE_ERROR"], "INVALID", 1
            return

        tx_nodes = root.findall(".//transaction")
        if not tx_nodes and root.tag == "transaction":
            tx_nodes = [root]

        for idx, tx_elem in enumerate(tx_nodes, start=1):
            try:
                row_dict: dict[str, Any] = {}
                for child in tx_elem:
                    tag = child.tag.lower()
                    if tag in ("inputs", "input_addresses"):
                        # Extract inputs
                        in_addrs = []
                        in_amts = []
                        for inp in child.findall("input"):
                            addr = inp.get("address") or inp.findtext("address")
                            amt = inp.get("amount") or inp.findtext("amount") or 0.0
                            if addr:
                                in_addrs.append(addr)
                                in_amts.append(float(amt))
                        if in_addrs:
                            row_dict["input_addresses"] = in_addrs
                            row_dict["input_amounts"] = in_amts
                        else:
                            row_dict["input_addresses"] = child.text
                    elif tag in ("outputs", "output_addresses"):
                        out_addrs = []
                        out_amts = []
                        for out in child.findall("output"):
                            addr = out.get("address") or out.findtext("address")
                            amt = out.get("amount") or out.findtext("amount") or 0.0
                            if addr:
                                out_addrs.append(addr)
                                out_amts.append(float(amt))
                        if out_addrs:
                            row_dict["output_addresses"] = out_addrs
                            row_dict["output_amounts"] = out_amts
                        else:
                            row_dict["output_addresses"] = child.text
                    else:
                        row_dict[tag] = child.text

                canonical, flags, status = normalize_raw_record(row_dict, source_file, idx)
                yield canonical, flags, status, idx
            except Exception as e:
                yield {"raw": ET.tostring(tx_elem, encoding="unicode"), "error": str(e)}, ["FLAG_XML_ROW_ERROR"], "INVALID", idx

    @classmethod
    def parse_file(
        cls, file_path: Path
    ) -> Generator[tuple[dict[str, Any], list[str], str, int], None, None]:
        with open(file_path, "rb") as f:
            content = f.read()
        yield from cls.parse_content(content, str(file_path))
