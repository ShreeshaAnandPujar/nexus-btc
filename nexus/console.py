"""NEXUS-BTC Interactive Linux Command Line Console.

Combines the modular exploit-framework command architecture of Metasploit (msfconsole)
with the intuitive numbered menu wizard workflows of Zphisher.
Air-gapped, offline-first digital forensics and Bitcoin transaction surveillance.
"""

import os
import sys
import cmd
import shlex
import time
from pathlib import Path
from typing import Optional, Dict, Any, List

# Ensure backend path is on sys.path
repo_root = Path(__file__).resolve().parent.parent
backend_path = repo_root / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn

from app.core.config import settings
from app.core.database import SessionLocal, init_db
from app.models.alert import AlertModel
from app.models.transaction import TransactionModel
from app.models.entity import EntityModel
from app.services.pipeline import ForensicPipeline
from app.services.scenario_generator import ScenarioGenerator
from app.schemas.scenario import ScenarioGenerateRequest
from app.tracing.best_first_tracer import BestFirstFundTracer
from app.schemas.trace import TraceRequest
from app.ingestion.engine import IngestionEngine

console = Console()

# ==============================================================================
# BANNERS & ASCII ART (Metasploit / Zphisher Style)
# ==============================================================================

BANNER_MSF = r"""[bold cyan]
  _   _ _______  ___   _ ____        ____ _____ ____ 
 | \ | | ____\ \/ / | | / ___|      | __ )_   _/ ___|
 |  \| |  _|  \  /| | | \___ \ _____|  _ \ | || |    
 | |\  | |___ /  \| |_| |___) |_____| |_) || || |___ 
 |_| \_|_____/_/\_\\___/|____/      |____/ |_| \____|
[/bold cyan][dim white] Network–Entity eXplainable Unified Surveillance for Bitcoin[/dim white]
[bold green] [AIR-GAPPED OFFLINE CONSOLE] [/bold green][bold yellow] [NTRO SIH 2026 PS-05] [/bold yellow][bold red] [CLEAN ROOM] [/bold red]
"""

BANNER_ZPHISHER = r"""[bold cyan]
  ╔═══════════════════════════════════════════════════════════════════════════╗
  ║   [bold white]NEXUS-BTC : FORENSIC SURVEILLANCE & AML COMMAND CONSOLE[/bold white]         ║
  ║   [dim white]Air-Gapped Offline Digital Forensics & Graph Intelligence System[/dim white]        ║
  ║   [bold green]100% Offline[/bold green] | [bold yellow]Zero CDN[/bold yellow] | [bold cyan]No External Telemetry[/bold cyan] | [bold magenta]MIT License[/bold magenta]            ║
  ╚═══════════════════════════════════════════════════════════════════════════╝[/bold cyan]
"""


def get_system_stats() -> Dict[str, Any]:
    """Fetch live counts from offline SQLite forensics database."""
    try:
        db = SessionLocal()
        tx_count = db.query(TransactionModel).count()
        alert_count = db.query(AlertModel).count()
        crit_count = db.query(AlertModel).filter(AlertModel.severity == "CRITICAL").count()
        entity_count = db.query(EntityModel).count()
        db.close()
        return {
            "tx_count": tx_count,
            "alert_count": alert_count,
            "crit_count": crit_count,
            "entity_count": entity_count,
            "motifs_count": 9,
            "models_count": 4,
            "scenarios_count": 12,
            "status": "HEALTHY",
        }
    except Exception as e:
        return {
            "tx_count": 0,
            "alert_count": 0,
            "crit_count": 0,
            "entity_count": 0,
            "motifs_count": 9,
            "models_count": 4,
            "scenarios_count": 12,
            "status": f"DB INIT ERROR: {e}",
        }


def print_msf_header():
    """Print the Metasploit-style ASCII banner and module stats block."""
    console.print(BANNER_MSF)
    stats = get_system_stats()
    stats_box = f"""       =[ [bold white]nexus-btc v1.0.0-offline[/bold white]                           ]
+ -- --=[ [bold green]{stats['motifs_count']} Laundering Motifs[/bold green]  | [bold cyan]{stats['models_count']} AI Inference Models[/bold cyan]   ]
+ -- --=[ [bold yellow]{stats['scenarios_count']} Adversarial Topologies[/bold yellow] | [bold magenta]SQLite3 (WAL Engine)[/bold magenta]       ]
+ -- --=[ [bold white]{stats['tx_count']} Stored TXs[/bold white] | [bold red]{stats['alert_count']} Alerts ({stats['crit_count']} Critical)[/bold red] | [bold blue]{stats['entity_count']} Entities[/bold blue] ]"""
    console.print(Panel(stats_box, border_style="cyan", padding=(0, 2)))
    console.print("[dim white]Type 'help' or '?' for commands. Type 'menu' for Zphisher-style numbered wizard.[/dim white]\n")


# ==============================================================================
# VISUALIZERS (ASCII SHAP, TRACE TREES, EVIDENCE CHAINS)
# ==============================================================================

def render_ascii_trace(result: Any):
    """Render Best-First Fund Tracer results as an ASCII flow sequence."""
    if not result.ranked_paths:
        console.print("[yellow][!] No downstream propagation paths discovered under active cutoff filters.[/yellow]")
        return

    console.print(f"\n[bold green][+] Tracer Discovered {len(result.ranked_paths)} Traversal Paths in {result.execution_time_ms:.1f}ms:[/bold green]\n")

    for idx, path in enumerate(result.ranked_paths, start=1):
        color = "red" if path.cumulative_risk >= 75 else "yellow" if path.cumulative_risk >= 50 else "green"
        console.print(f"[bold cyan]PATH #{idx}[/bold cyan] ({path.path_length} hops, Terminal: [bold {color}]{path.endpoint_type}[/bold {color}], Volume: [bold white]{path.total_btc_traced:.4f} BTC[/bold white], Risk: [{color}]{path.cumulative_risk:.1f}[/{color}]):")

        # Visual chain
        for h_idx, hop in enumerate(path.hops):
            h_color = "red" if hop.hop_risk >= 75 else "yellow" if hop.hop_risk >= 50 else "cyan"
            indent = "  " * (h_idx + 1)
            arrow = "└──►" if h_idx > 0 else "┌───"
            console.print(f"{indent}{arrow} [dim]Hop {hop.hop_index}:[/dim] [green]{hop.from_wallet}[/green] ──([bold white]{hop.amount_btc:.4f} BTC[/bold white])──► [green]{hop.to_wallet}[/green] [dim](TX: {hop.txid[:10]}...)[/dim] [{h_color}]Risk: {hop.hop_risk:.1f}[/{h_color}]")
        console.print()


def render_ascii_shap(explanation: Dict[str, Any]):
    """Render an ASCII horizontal bar chart for SHAP feature attributions."""
    attributions = explanation.get("top_feature_attributions", [])
    base_val = explanation.get("base_expected_value", 18.5)
    final_risk = explanation.get("final_risk_score", 0.0)

    console.print(f"\n[bold cyan]SHAP TreeExplainer Attribution Waterfall[/bold cyan] (Base: {base_val:.1f} ──► Final Risk: [bold red]{final_risk:.1f}[/bold red]):")

    table = Table(show_header=True, header_style="bold magenta", border_style="dim")
    table.add_column("Forensic Feature", style="white")
    table.add_column("Value", justify="right", style="cyan")
    table.add_column("Contribution", justify="right")
    table.add_column("Attribution Magnitude Bar", style="dim")

    for attr in attributions:
        contrib = attr.get("contribution", 0.0)
        disp_name = attr.get("display_name", attr.get("feature_name", ""))
        val = attr.get("feature_value", 0.0)

        # Bar generation
        bar_len = min(int(abs(contrib) * 2), 25)
        if contrib >= 0:
            bar = f"[red]{'█' * bar_len}[/red]"
            contrib_str = f"[bold red]+{contrib:.2f}[/bold red]"
        else:
            bar = f"[green]{'█' * bar_len}[/green]"
            contrib_str = f"[bold green]{contrib:.2f}[/bold green]"

        table.add_row(disp_name, f"{val:.2f}", contrib_str, bar)

    console.print(table)


# ==============================================================================
# METASPLOIT-STYLE COMMAND LINE SHELL (cmd.Cmd)
# ==============================================================================

class NexusMSFConsole(cmd.Cmd):
    """Metasploit-style interactive forensic console."""

    prompt = "[bold cyan]nexus-btc[/bold cyan] > "

    def __init__(self):
        super().__init__()
        self.active_module: Optional[str] = None
        self.module_options: Dict[str, Dict[str, Any]] = {}
        self.init_modules()

    def init_modules(self):
        """Define available exploit/forensic modules with options."""
        self.modules = {
            "forensics/pipeline": {
                "desc": "Execute master 14-stage forensic analysis pipeline",
                "options": {},
                "runner": self.run_pipeline_module,
            },
            "tracing/best_first": {
                "desc": "Value-aware best-first UTXO money flow tracer",
                "options": {
                    "TARGET": {"value": "", "req": True, "desc": "Wallet address or Transaction Hash (64 hex)"},
                    "TYPE": {"value": "wallet", "req": True, "desc": "Target type: wallet | txid | entity"},
                    "HOPS": {"value": 8, "req": False, "desc": "Maximum search depth hops (1-25)"},
                    "NODES": {"value": 60, "req": False, "desc": "Maximum traversal node budget"},
                    "CUTOFF": {"value": 0.01, "req": False, "desc": "Minimum UTXO value fraction cutoff (0.01 = 1%)"},
                },
                "runner": self.run_tracer_module,
            },
            "investigation/deep_inspect": {
                "desc": "Deep transaction & relay telemetry inspector",
                "options": {
                    "TARGET": {"value": "", "req": True, "desc": "TXID hash (64 hex), wallet address, or relay IP"},
                },
                "runner": self.run_investigate_module,
            },
            "explainability/shap": {
                "desc": "Multimodal SHAP waterfall attributions & counterfactuals",
                "options": {
                    "ALERT_ID": {"value": "", "req": True, "desc": "Forensic Alert ID (e.g. ALT-1234)"},
                },
                "runner": self.run_explain_module,
            },
            "scenarios/adversarial": {
                "desc": "Synthetic adversarial scenario generator (12 topologies)",
                "options": {
                    "TYPE": {"value": "PEELING_CHAIN", "req": True, "desc": "Scenario name: PEELING_CHAIN, FAN_IN, MIXING_LIKE, etc."},
                    "COUNT": {"value": 15, "req": False, "desc": "Number of transactions to synthesize"},
                    "SEED": {"value": 42, "req": False, "desc": "Deterministic pseudo-random seed"},
                    "VOLUME": {"value": 10.0, "req": False, "desc": "Base Bitcoin volume (BTC)"},
                },
                "runner": self.run_scenario_module,
            },
            "ingest/multiformat": {
                "desc": "Multi-format safe transaction ingestion engine",
                "options": {
                    "FILE": {"value": "data/sample/transactions_sample.csv", "req": True, "desc": "Path to CSV, JSON, or XML transaction batch"},
                    "ANALYZE": {"value": True, "req": False, "desc": "Automatically trigger forensic pipeline"},
                },
                "runner": self.run_ingest_module,
            },
        }

    def update_prompt(self):
        if self.active_module:
            # Colorized active module prompt like msfconsole
            mod_short = self.active_module.split("/")[-1]
            self.prompt = f"\033[1;36mnexus-btc\033[0m (\033[1;31m{mod_short}\033[0m) > "
        else:
            self.prompt = "\033[1;36mnexus-btc\033[0m > "

    def default(self, line: str):
        if line.strip() == "":
            return
        console.print(f"[bold red][-] Unknown command:[/bold red] '{line}'. Type [bold cyan]help[/bold cyan] or [bold cyan]?[/bold cyan] for available commands.")

    def do_banner(self, arg):
        """Display NEXUS-BTC console banner."""
        print_msf_header()

    def do_clear(self, arg):
        """Clear terminal screen."""
        os.system("clear" if os.name != "nt" else "cls")
        print_msf_header()

    def do_menu(self, arg):
        """Switch to Zphisher-style numbered wizard menu."""
        wizard = NexusZphisherMenu()
        wizard.run()
        self.update_prompt()

    def do_status(self, arg):
        """Show full system health, models status, and offline compliance."""
        stats = get_system_stats()
        table = Table(title="NEXUS-BTC Subsystem Diagnostics", border_style="cyan")
        table.add_column("Subsystem", style="magenta")
        table.add_column("Status / Metric", style="green")
        table.add_column("Governance", style="dim")

        table.add_row("Deployment Mode", "AIR-GAPPED OFFLINE", "Zero CDN, Zero Cloud APIs")
        table.add_row("Database Engine", "SQLite 3 (WAL mode)", settings.DATABASE_URL.split("///")[-1])
        table.add_row("Transactions Stored", str(stats["tx_count"]), "Canonical on-chain records")
        table.add_row("Active Alerts", f"{stats['alert_count']} ({stats['crit_count']} CRITICAL)", "Prioritized Risk & Conf")
        table.add_row("Entity Clusters", str(stats["entity_count"]), "Common-Input Disjoint Union")
        table.add_row("AI Models Zoo", "4 Loaded Models", "IForest + Platt-RF + Velocity + SHAP")
        table.add_row("Laundering Motifs", "9 Active Detectors", "Peeling, CoinJoin, Fan-In, Cycles...")
        table.add_row("Academic Alignment", "NTRO SIH 2026 PS-05", "Clean Room Reimplementation")
        console.print(table)

    def do_use(self, arg: str):
        """Select a forensic module to configure and run (e.g. 'use tracing/best_first')."""
        target = arg.strip()
        if not target:
            console.print("[yellow][!] Usage: use <module_name>. Available modules:[/yellow]")
            for k, m in self.modules.items():
                console.print(f"  • [cyan]{k:<30}[/cyan] {m['desc']}")
            return

        # Partial matching support
        matches = [k for k in self.modules if target in k or k.endswith(target)]
        if not matches:
            console.print(f"[bold red][-] Module '{target}' not found.[/bold red] Type 'show modules' to view catalog.")
            return

        selected = matches[0]
        self.active_module = selected
        self.module_options = {k: dict(v) for k, v in self.modules[selected]["options"].items()}
        self.update_prompt()
        console.print(f"[bold green][*] Using module {selected}[/bold green]")
        self.do_show("options")

    def complete_use(self, text, line, begidx, endidx):
        return [k for k in self.modules if k.startswith(text)]

    def do_back(self, arg):
        """Exit current module context back to root prompt."""
        self.active_module = None
        self.module_options = {}
        self.update_prompt()

    def do_set(self, arg: str):
        """Set a module option value (e.g. 'set TARGET 1PeelOrigin_42')."""
        if not self.active_module:
            console.print("[yellow][!] No module active. Use 'use <module>' first.[/yellow]")
            return

        parts = arg.strip().split(maxsplit=1)
        if len(parts) < 2:
            console.print("[yellow][!] Usage: set <OPTION_NAME> <VALUE>[/yellow]")
            return

        opt_name = parts[0].upper()
        opt_val = parts[1]

        if opt_name not in self.module_options:
            console.print(f"[bold red][-] Unknown option '{opt_name}'.[/bold red] Type 'show options' to view options.")
            return

        # Type conversion
        curr_val = self.module_options[opt_name]["value"]
        if isinstance(curr_val, int):
            try:
                opt_val = int(opt_val)
            except ValueError:
                pass
        elif isinstance(curr_val, float):
            try:
                opt_val = float(opt_val)
            except ValueError:
                pass
        elif isinstance(curr_val, bool):
            opt_val = opt_val.lower() in ("true", "1", "yes")

        self.module_options[opt_name]["value"] = opt_val
        console.print(f"[bold cyan]{opt_name}[/bold cyan] => [bold white]{opt_val}[/bold white]")

    def complete_set(self, text, line, begidx, endidx):
        if not self.active_module:
            return []
        return [k for k in self.module_options if k.startswith(text.upper())]

    def do_run(self, arg):
        """Execute active module (alias: exploit, analyze)."""
        if not self.active_module:
            console.print("[yellow][!] No module active. Use 'use <module>' or execute direct commands.[/yellow]")
            return

        # Check required options
        for opt, meta in self.module_options.items():
            if meta.get("req") and (meta["value"] is None or str(meta["value"]).strip() == ""):
                console.print(f"[bold red][-] Required option '{opt}' is not set.[/bold red]")
                return

        runner = self.modules[self.active_module]["runner"]
        runner()

    do_exploit = do_run
    do_analyze = do_run

    # ---------------- Module Runners ----------------

    def run_pipeline_module(self):
        console.print("[bold cyan][*] Launching 14-Stage Forensic Pipeline...[/bold cyan]")
        p = ForensicPipeline()
        summary = p.run_full_pipeline()
        console.print(f"[bold green][+] Analysis completed in {summary.get('execution_time_seconds', 0):.2f}s[/bold green]")
        console.print(f"  • Analyzed Transactions: [white]{summary.get('transactions_analyzed', 0)}[/white]")
        console.print(f"  • Clustered Entities:    [white]{summary.get('entities_clustered', 0)}[/white]")
        console.print(f"  • Alerts Generated:      [bold red]{summary.get('alerts_generated', 0)}[/bold red] ([red]{summary.get('critical_alerts', 0)} Critical[/red], [yellow]{summary.get('high_alerts', 0)} High[/yellow])")

    def run_tracer_module(self):
        target = str(self.module_options["TARGET"]["value"]).strip()
        t_type = str(self.module_options["TYPE"]["value"]).strip()
        hops = int(self.module_options["HOPS"]["value"])
        nodes = int(self.module_options["NODES"]["value"])
        cutoff = float(self.module_options["CUTOFF"]["value"])

        console.print(f"[bold cyan][*] Executing Value-Aware Best-First Tracer on {t_type} '{target}'...[/bold cyan]")
        db = SessionLocal()
        tracer = BestFirstFundTracer(db=db)
        req = TraceRequest(
            start_type=t_type,
            start_identifier=target,
            max_hops=hops,
            max_nodes=nodes,
            min_value_ratio=cutoff,
        )
        res = tracer.trace(req)
        db.close()
        render_ascii_trace(res)

    def run_investigate_module(self):
        target = str(self.module_options["TARGET"]["value"]).strip()
        self.do_investigate(target)

    def run_explain_module(self):
        alert_id = str(self.module_options["ALERT_ID"]["value"]).strip()
        self.do_explain(alert_id)

    def run_scenario_module(self):
        s_type = str(self.module_options["TYPE"]["value"]).strip()
        count = int(self.module_options["COUNT"]["value"])
        seed = int(self.module_options["SEED"]["value"])
        vol = float(self.module_options["VOLUME"]["value"])
        self.do_scenario(f"{s_type} {count} {seed} {vol}")

    def run_ingest_module(self):
        file_path = str(self.module_options["FILE"]["value"]).strip()
        analyze = bool(self.module_options["ANALYZE"]["value"])
        self.do_ingest(f"{file_path} {'--analyze' if analyze else '--no-analyze'}")

    # ---------------- Direct Global Commands ----------------

    def do_show(self, arg: str):
        """Show forensic data or module info: show <options|modules|alerts|entities|transactions|motifs|scenarios|models>"""
        tokens = arg.strip().split()
        cmd_type = tokens[0].lower() if tokens else ""

        if cmd_type == "options":
            if not self.active_module:
                console.print("[yellow][!] No module active. Use 'use <module>' first.[/yellow]")
                return
            table = Table(title=f"Module Options ({self.active_module})", border_style="cyan")
            table.add_column("Option Name", style="bold magenta")
            table.add_column("Current Setting", style="white")
            table.add_column("Required", style="yellow")
            table.add_column("Description", style="dim")
            for k, v in self.module_options.items():
                table.add_row(k, str(v["value"]), "yes" if v["req"] else "no", v["desc"])
            console.print(table)

        elif cmd_type == "modules":
            table = Table(title="NEXUS-BTC Forensic Modules Catalog", border_style="cyan")
            table.add_column("Module Path", style="bold cyan")
            table.add_column("Description", style="white")
            for k, v in self.modules.items():
                table.add_row(k, v["desc"])
            console.print(table)

        elif cmd_type in ("alerts", "alert"):
            sev = tokens[1].upper() if len(tokens) > 1 and tokens[1].upper() in ("CRITICAL", "HIGH", "MEDIUM", "LOW") else None
            db = SessionLocal()
            q = db.query(AlertModel)
            if sev:
                q = q.filter(AlertModel.severity == sev)
            alerts = q.order_by(AlertModel.risk_score.desc()).limit(25).all()

            table = Table(title=f"Ranked Alert Queue ({len(alerts)} displayed)", border_style="red")
            table.add_column("Alert ID", style="bold cyan")
            table.add_column("TXID Hash", style="dim")
            table.add_column("Motif", style="magenta")
            table.add_column("Severity", style="bold")
            table.add_column("Risk Score", justify="right")
            table.add_column("Confidence", justify="right", style="cyan")

            for a in alerts:
                s_color = "red" if a.severity == "CRITICAL" else "yellow" if a.severity == "HIGH" else "blue"
                r_color = "bold red" if a.risk_score >= 80 else "yellow" if a.risk_score >= 65 else "green"
                table.add_row(
                    a.alert_id,
                    f"{a.txid[:10]}...{a.txid[-6:]}",
                    a.primary_motif or "ANOMALY",
                    f"[{s_color}]{a.severity}[/{s_color}]",
                    f"[{r_color}]{a.risk_score:.1f}[/{r_color}]",
                    f"{a.confidence_score:.1f}%",
                )
            db.close()
            console.print(table)

        elif cmd_type in ("entities", "entity"):
            db = SessionLocal()
            ents = db.query(EntityModel).order_by(EntityModel.risk_score.desc()).limit(20).all()
            table = Table(title=f"Inferred Entity Clusters ({len(ents)} displayed)", border_style="green")
            table.add_column("Entity ID", style="bold green")
            table.add_column("Cluster Type", style="cyan")
            table.add_column("Wallets", justify="right")
            table.add_column("Volume (BTC)", justify="right")
            table.add_column("Risk Score", justify="right")

            for e in ents:
                r_color = "red" if e.risk_score >= 75 else "yellow" if e.risk_score >= 50 else "green"
                table.add_row(
                    e.entity_id,
                    e.cluster_type.replace("_", " "),
                    str(e.wallet_count),
                    f"{e.total_volume_btc:.4f}",
                    f"[{r_color}]{e.risk_score:.1f}[/{r_color}]",
                )
            db.close()
            console.print(table)

        elif cmd_type in ("transactions", "tx"):
            db = SessionLocal()
            txs = db.query(TransactionModel).order_by(TransactionModel.timestamp.desc()).limit(20).all()
            table = Table(title=f"Monitored Transactions ({len(txs)} displayed)", border_style="blue")
            table.add_column("TXID Hash", style="bold cyan")
            table.add_column("Relay IP", style="yellow")
            table.add_column("Country", style="green")
            table.add_column("Volume (BTC)", justify="right")
            table.add_column("Fee (BTC)", justify="right", style="dim")
            table.add_column("Risk", justify="right")

            for t in txs:
                r_color = "red" if t.risk_score >= 75 else "yellow" if t.risk_score >= 50 else "green"
                table.add_row(
                    f"{t.txid[:12]}...{t.txid[-6:]}",
                    t.src_ip,
                    t.country,
                    f"{t.output_amount:.4f}",
                    f"{t.fee:.6f}",
                    f"[{r_color}]{t.risk_score:.1f}[/{r_color}]",
                )
            db.close()
            console.print(table)

        elif cmd_type in ("motifs", "motif"):
            motifs = [
                ("PEELING_CHAIN", "Iterative incremental peeling of small amounts into change addresses"),
                ("MIXING_LIKE", "CoinJoin-style equal output denomination multi-party mixing transactions"),
                ("FAN_IN", "Consolidation of scattered UTXOs from multiple sources into a single sink wallet"),
                ("FAN_OUT", "Rapid dispersion of funds from single source to diverse downstream accounts"),
                ("RAPID_LAYERING", "High-frequency multi-hop transfers to evade temporal correlation"),
                ("CIRCULAR_FLOW", "Cyclic fund movement returning to origin wallet or cluster"),
                ("DORMANT_ACTIVATION", "Sudden reactivation of long-idle UTXOs (>180 days) followed by movement"),
                ("SUSPICIOUS_CONSOLIDATION", "Consolidation of fragmented high-risk funds without apparent retail purpose"),
                ("RAPID_SPLIT", "Instantaneous split into distinct equal-value splits within single block"),
            ]
            table = Table(title="NEXUS-BTC 9 Money Laundering Motif Detectors", border_style="magenta")
            table.add_column("Motif Name", style="bold magenta")
            table.add_column("Forensic Pattern Description", style="white")
            for m, d in motifs:
                table.add_row(m, d)
            console.print(table)

        elif cmd_type in ("scenarios", "scenario"):
            table = Table(title="NEXUS-BTC 12 Synthetic Adversarial Topologies", border_style="yellow")
            table.add_column("Scenario ID", style="bold cyan")
            table.add_column("Title", style="white")
            table.add_column("Ground Truth", style="bold")
            table.add_column("Expected Motifs", style="magenta")

            for s in ScenarioGenerator.SCENARIO_CATALOG.values():
                gt_str = "[red]ILLICIT[/red]" if s.ground_truth_illicit else "[green]BENIGN[/green]"
                table.add_row(s.scenario_id, s.title, gt_str, ", ".join(s.expected_motifs) or "BENIGN")
            console.print(table)

        elif cmd_type in ("models", "metrics"):
            from app.api.models import get_model_metrics
            db = SessionLocal()
            metrics = get_model_metrics(db=db)
            db.close()
            m_vals = metrics.get("metrics", {}) if isinstance(metrics, dict) else metrics.metrics
            cm = m_vals.get("confusion_matrix", {}) if isinstance(m_vals, dict) else m_vals.confusion_matrix

            table = Table(title="AI Models Evaluation Metrics (Chronological Validation Split)", border_style="green")
            table.add_column("Evaluation Metric", style="cyan")
            table.add_column("Measured Value", style="bold white")
            table.add_column("Forensic Interpretation", style="dim")

            prec = m_vals.get("precision", 0.0) if isinstance(m_vals, dict) else m_vals.precision
            rec = m_vals.get("recall", 0.0) if isinstance(m_vals, dict) else m_vals.recall
            f1 = m_vals.get("f1_score", 0.0) if isinstance(m_vals, dict) else m_vals.f1_score
            roc = m_vals.get("roc_auc", 0.0) if isinstance(m_vals, dict) else m_vals.roc_auc
            pr = m_vals.get("pr_auc", 0.0) if isinstance(m_vals, dict) else m_vals.pr_auc
            brier = m_vals.get("brier_score", 0.0) if isinstance(m_vals, dict) else m_vals.brier_score
            thresh = m_vals.get("decision_threshold", 0.5) if isinstance(m_vals, dict) else m_vals.decision_threshold

            table.add_row("Precision", f"{prec*100:.1f}%", "Positive predictive value (Low false alarms)")
            table.add_row("Recall (Sensitivity)", f"{rec*100:.1f}%", "Illicit hop detection rate")
            table.add_row("F1-Score", f"{f1*100:.1f}%", "Harmonic mean balance")
            table.add_row("ROC-AUC / PR-AUC", f"{roc:.2f} / {pr:.2f}", "Separation on imbalanced labels")
            table.add_row("Brier Score Loss", f"{brier:.3f}", "Platt calibration fidelity (<0.1)")
            table.add_row("Decision Threshold", f"{thresh:.2f}", "Orthogonal threshold cutoff")
            console.print(table)

            cm_table = Table(title="Confusion Matrix", border_style="yellow")
            cm_table.add_column("Matrix Cell", style="magenta")
            cm_table.add_column("Count", justify="right", style="bold white")
            tp = cm.get("true_positives", 0) if isinstance(cm, dict) else cm.true_positives
            fp = cm.get("false_positives", 0) if isinstance(cm, dict) else cm.false_positives
            fn = cm.get("false_negatives", 0) if isinstance(cm, dict) else cm.false_negatives
            tn = cm.get("true_negatives", 0) if isinstance(cm, dict) else cm.true_negatives
            cm_table.add_row("True Positives (TP)", f"[green]{tp}[/green]")
            cm_table.add_row("False Positives (FP)", f"[yellow]{fp}[/yellow]")
            cm_table.add_row("False Negatives (FN)", f"[red]{fn}[/red]")
            cm_table.add_row("True Negatives (TN)", f"[cyan]{tn}[/cyan]")
            console.print(cm_table)


        else:
            console.print("[yellow][!] Available show targets: options, modules, alerts, entities, transactions, motifs, scenarios, models[/yellow]")

    def complete_show(self, text, line, begidx, endidx):
        targets = ["options", "modules", "alerts", "entities", "transactions", "motifs", "scenarios", "models"]
        return [t for t in targets if t.startswith(text.lower())]

    def do_trace(self, arg: str):
        """Trace funds from wallet or TXID: trace <identifier> [max_hops] [wallet|txid]"""
        parts = arg.strip().split()
        if not parts:
            console.print("[yellow][!] Usage: trace <wallet_or_txid> [hops=8] [type=wallet|txid][/yellow]")
            return

        ident = parts[0]
        hops = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 8
        t_type = parts[2] if len(parts) > 2 else ("txid" if len(ident) == 64 else "wallet")

        db = SessionLocal()
        tracer = BestFirstFundTracer(db=db)
        req = TraceRequest(start_type=t_type, start_identifier=ident, max_hops=hops, max_nodes=60, min_value_ratio=0.01)
        res = tracer.trace(req)
        db.close()
        render_ascii_trace(res)

    def do_investigate(self, arg: str):
        """Deep forensic inspection: investigate <txid_or_wallet_or_ip>"""
        ident = arg.strip()
        if not ident:
            console.print("[yellow][!] Usage: investigate <txid|wallet|ip>[/yellow]")
            return

        db = SessionLocal()
        # Search transactions
        tx = db.query(TransactionModel).filter(TransactionModel.txid == ident).first()
        if not tx:
            # Try search by prefix or IP
            tx = db.query(TransactionModel).filter(
                (TransactionModel.txid.like(f"%{ident}%")) |
                (TransactionModel.src_ip == ident)
            ).first()

        if not tx:
            console.print(f"[bold red][-] No transaction record found matching '{ident}'.[/bold red]")
            db.close()
            return

        console.print(f"\n[bold cyan]Forensic Transaction Dossier[/bold cyan] : [bold white]{tx.txid}[/bold white]")

        info_table = Table(show_header=False, border_style="cyan")
        info_table.add_column("Field", style="magenta")
        info_table.add_column("Value", style="white")

        info_table.add_row("Timestamp", str(tx.timestamp))
        info_table.add_row("Output Volume", f"[bold white]{tx.output_amount:.4f} BTC[/bold white]")
        info_table.add_row("Miner Fee", f"{tx.fee:.6f} BTC")
        info_table.add_row("Script Type", tx.script_type)
        info_table.add_row("Risk Score", f"[{'red' if tx.risk_score>=75 else 'yellow'}]{tx.risk_score:.1f} / 100[/{'red' if tx.risk_score>=75 else 'yellow'}]")
        info_table.add_row("Relay IP", f"{tx.src_ip} [dim](Country: {tx.country}, ASN: AS{tx.asn})[/dim]")
        info_table.add_row("Clustered Entity", tx.entity_id or "Unclustered")
        console.print(info_table)

        # Inputs and outputs
        io_table = Table(title="Inputs & Outputs Topology", border_style="dim")
        io_table.add_column("Direction", style="bold")
        io_table.add_column("Address", style="cyan")
        io_table.add_column("Amount (BTC)", justify="right", style="white")

        for addr, amt in zip(tx.input_addresses, tx.input_amounts):
            io_table.add_row("[blue]INPUT[/blue]", addr, f"{amt:.4f}")
        for addr, amt in zip(tx.output_addresses, tx.output_amounts):
            io_table.add_row("[green]OUTPUT[/green]", addr, f"{amt:.4f}")

        console.print(io_table)
        db.close()

    def do_explain(self, arg: str):
        """Inspect SHAP attributions & counterfactuals: explain <alert_id_or_txid>"""
        ident = arg.strip()
        if not ident:
            console.print("[yellow][!] Usage: explain <alert_id>[/yellow]")
            return

        db = SessionLocal()
        alert = db.query(AlertModel).filter(AlertModel.alert_id == ident).first()
        if not alert:
            alert = db.query(AlertModel).filter(AlertModel.txid.like(f"%{ident}%")).first()

        if not alert:
            console.print(f"[bold red][-] Alert '{ident}' not found.[/bold red]")
            db.close()
            return

        console.print(f"\n[bold cyan]Forensic Alert Dossier[/bold cyan] : [bold white]{alert.alert_id}[/bold white] (TXID: {alert.txid[:12]}...)")
        console.print(f"Severity: [bold red]{alert.severity}[/bold red] | Risk: [bold red]{alert.risk_score:.1f}[/bold red] | Confidence: [bold cyan]{alert.confidence_score:.1f}%[/bold cyan] | Primary Motif: [magenta]{alert.primary_motif}[/magenta]")

        if alert.explanation:
            render_ascii_shap(alert.explanation)

        if alert.counterfactual:
            console.print("\n[bold cyan]Counterfactual Sensitivity Analysis (What-If Perturbations):[/bold cyan]")
            cf_table = Table(show_header=True, border_style="dim")
            cf_table.add_column("Perturbation", style="magenta")
            cf_table.add_column("Risk Delta", style="bold green")
            cf_table.add_column("Forensic Interpretation", style="white")
            for cf in alert.counterfactual:
                cf_table.add_row(cf.get("modified_feature_name", ""), f"{cf.get('delta', 0.0):.1f} pts", cf.get("interpretation", ""))
            console.print(cf_table)

        if alert.evidence_chain:
            console.print("\n[bold cyan]Forensic Evidence Chain Stages:[/bold cyan]")
            for step in alert.evidence_chain:
                step_no = step.get("step_number", step.get("stage", 1))
                step_type = step.get("step_type", step.get("title", "STAGE")).replace("_", " ")
                detail = step.get("description", step.get("detail", ""))
                conf = step.get("confidence", 1.0)
                flag_str = "[bold red][FLAG][/bold red]" if conf >= 0.7 or "ALERT" in step_type or "MOTIF" in step_type else "[bold green][OK][/bold green]"
                console.print(f"  {flag_str} [bold white]Step {step_no}: {step_type}[/bold white] (Conf: {conf*100:.0f}%) ── [dim]{detail}[/dim]")

        db.close()


    def do_scenario(self, arg: str):
        """Generate and inject synthetic scenario: scenario <type> [count] [seed] [volume]"""
        parts = arg.strip().split()
        s_type = parts[0].upper() if parts else "PEELING_CHAIN"
        count = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 15
        seed = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 42
        vol = float(parts[3]) if len(parts) > 3 else 10.0

        console.print(f"[bold cyan][*] Synthesizing scenario '{s_type}' ({count} TXs, seed={seed})...[/bold cyan]")
        gen = ScenarioGenerator()
        req = ScenarioGenerateRequest(scenario_type=s_type, seed=seed, transaction_count=count, base_volume_btc=vol)
        resp, recs = gen.generate(req)

        # Ingest into db
        import json
        db = SessionLocal()
        engine = IngestionEngine(db=db)
        ingest_res = engine.ingest_content(
            content=json.dumps(recs),
            source_name=f"cli_scenario_{s_type.lower()}_{seed}.json",
            format_hint="json",
        )
        pipeline = ForensicPipeline(db=db)
        summary = pipeline.run_full_pipeline()
        db.close()

        console.print(f"[bold green][+] Successfully generated & analyzed scenario {s_type}![/bold green]")
        console.print(f"  • Valid Records Ingested: {ingest_res.records_valid}")
        gt_color = "bold red" if resp.ground_truth_label == "ILLICIT" else "bold green"
        console.print(f"  • Ground Truth Label: [{gt_color}]{resp.ground_truth_label}[/{gt_color}]")
        console.print(f"  • Expected Motifs: [magenta]{', '.join(resp.expected_motifs)}[/magenta]")
        console.print(f"  • Pipeline Result: {summary.get('alerts_generated', 0)} alerts ({summary.get('critical_alerts', 0)} Critical)")


    def complete_scenario(self, text, line, begidx, endidx):
        types = list(ScenarioGenerator.SCENARIO_CATALOG.keys())
        return [t for t in types if t.startswith(text.upper())]

    def do_ingest(self, arg: str):
        """Ingest transaction file: ingest <filepath_or_sample> [--analyze/--no-analyze]"""
        parts = arg.strip().split()
        if not parts:
            console.print("[yellow][!] Usage: ingest <file_path|sample> [--no-analyze][/yellow]")
            return

        target = parts[0]
        analyze = "--no-analyze" not in parts

        if target.lower() == "sample":
            target = str(repo_root / "data" / "sample" / "transactions_sample.csv")

        p = Path(target)
        if not p.exists():
            console.print(f"[bold red][-] File not found:[/bold red] {target}")
            return

        console.print(f"[bold cyan][*] Ingesting {p.name}...[/bold cyan]")
        db = SessionLocal()
        engine = IngestionEngine(db=db)
        result = engine.ingest_file(p)

        console.print(f"[bold green][+] Ingested {result.records_valid} records ({result.records_invalid} quarantined, {result.duplicates} duplicates filtered)[/bold green]")
        if analyze and result.records_valid > 0:
            console.print("[bold cyan][*] Triggering forensic pipeline...[/bold cyan]")
            pipeline = ForensicPipeline(db=db)
            summary = pipeline.run_full_pipeline()
            console.print(f"[bold green][+] Pipeline complete: {summary.get('alerts_generated', 0)} alerts generated.[/bold green]")
        db.close()

    def do_pipeline(self, arg):
        """Run master 14-stage forensic pipeline across all stored transactions."""
        self.run_pipeline_module()

    def do_serve(self, arg: str):
        """Start local offline FastAPI backend web server: serve [--host 127.0.0.1] [--port 8000]"""
        import uvicorn
        port = 8000
        host = "127.0.0.1"
        parts = arg.strip().split()
        for idx, part in enumerate(parts):
            if part in ("--port", "-p") and idx + 1 < len(parts):
                port = int(parts[idx + 1])
            elif part in ("--host", "-h") and idx + 1 < len(parts):
                host = parts[idx + 1]

        console.print(f"[bold green][+] Starting NEXUS-BTC local web server at http://{host}:{port}[/bold green]")
        console.print("[dim]Press Ctrl+C to stop web server and return to console.[/dim]")
        try:
            uvicorn.run("app.main:app", host=host, port=port, reload=False)
        except KeyboardInterrupt:
            console.print("\n[yellow][*] Web server stopped.[/yellow]")

    def do_help(self, arg: str):
        """Display help menu."""
        if arg.strip():
            super().do_help(arg)
            return

        table = Table(title="NEXUS-BTC Interactive Console Commands", border_style="cyan")
        table.add_column("Command", style="bold cyan")
        table.add_column("Arguments", style="yellow")
        table.add_column("Description", style="white")

        table.add_row("help / ?", "[command]", "Display this help reference")
        table.add_row("banner", "", "Display NEXUS-BTC ASCII banner")
        table.add_row("status", "", "Check system health, database, and model readiness")
        table.add_row("use", "<module_name>", "Select and enter a forensic module context")
        table.add_row("show", "<options|alerts|entities|txs|motifs|scenarios|models>", "Inspect forensic queue, entities, or catalog")
        table.add_row("set", "<OPTION> <VALUE>", "Set configuration option within active module")
        table.add_row("run / exploit", "", "Execute current active module")
        table.add_row("back", "", "Return to root prompt from active module")
        table.add_row("trace", "<target> [hops] [type]", "Value-Aware Best-First Fund Tracer")
        table.add_row("investigate", "<txid|addr|ip>", "Deep transaction & relay telemetry inspector")
        table.add_row("explain", "<alert_id>", "SHAP feature attributions & counterfactuals")
        table.add_row("scenario", "<type> [count] [seed]", "Synthesize deterministic adversarial scenario")
        table.add_row("ingest", "<filepath|sample>", "Multi-format safe transaction ingestion")
        table.add_row("pipeline", "", "Execute full 14-stage master forensic pipeline")
        table.add_row("serve", "[--port 8000]", "Launch local offline command center web server")
        table.add_row("menu", "", "Switch to Zphisher-style numbered wizard menu")
        table.add_row("clear", "", "Clear terminal screen")
        table.add_row("exit / quit", "", "Exit NEXUS-BTC console")

        console.print(table)
        console.print("[dim white]Protip: Tab-completion is enabled for all commands, modules, and options.[/dim white]\n")

    def do_exit(self, arg):
        """Exit NEXUS-BTC console."""
        console.print("\n[bold cyan][*] Exiting NEXUS-BTC Console. Goodbye![/bold cyan]")
        return True

    do_quit = do_exit
    do_EOF = do_exit


# ==============================================================================
# ZPHISHER-STYLE NUMBERED MENU WIZARD
# ==============================================================================

class NexusZphisherMenu:
    """Zphisher-style interactive numbered menu wizard."""

    def __init__(self):
        self.msf = NexusMSFConsole()

    def print_menu(self):
        console.print(BANNER_ZPHISHER)
        stats = get_system_stats()
        console.print(f" [dim]DB Status: [green]{stats['status']}[/green] | Records: [white]{stats['tx_count']} TXs[/white] | Alerts: [red]{stats['alert_count']}[/red] | Entities: [cyan]{stats['entity_count']}[/cyan][/dim]\n")

        menu_items = [
            ("[01]", "Master Forensic Pipeline (Execute 14-Stage Analysis)"),
            ("[02]", "Value-Aware Best-First Fund Tracer (Forward UTXO Traversal)"),
            ("[03]", "Digital Forensics Investigator (TXID / Wallet / Relay IP)"),
            ("[04]", "Ranked Alert Queue & Forensic Dossier Review"),
            ("[05]", "Inferred Entity Clusters & Common-Input Explorer"),
            ("[06]", "Multimodal Explainability Studio (SHAP & Counterfactuals)"),
            ("[07]", "Synthetic Adversarial Scenario Topologies (12 Models)"),
            ("[08]", "Machine Learning Benchmark & Calibration Metrics"),
            ("[09]", "Ingest Transaction Dataset (CSV / JSON / XML)"),
            ("[10]", "Load Bundled Forensic Sample Dataset"),
            ("[11]", "Launch Local Air-Gapped Web Command Center"),
            ("[12]", "Switch to MSF-Style Interactive Console (nexus-btc >)"),
            ("[00]", "Exit NEXUS-BTC Console"),
        ]

        for num, text in menu_items:
            console.print(f" [bold cyan]{num}[/bold cyan] [bold white]{text}[/bold white]")
        console.print()

    def run(self):
        while True:
            self.print_menu()
            choice = input("\033[1;32mnexus-btc\033[0m \033[1;33m>>\033[0m Select an option [00-12]: ").strip()

            if choice in ("00", "0", "exit", "quit", "q"):
                console.print("\n[bold cyan][*] Exiting NEXUS-BTC. Goodbye![/bold cyan]")
                sys.exit(0)

            elif choice in ("01", "1"):
                console.print("\n[bold cyan][*] Executing Master Forensic Pipeline...[/bold cyan]")
                self.msf.run_pipeline_module()

            elif choice in ("02", "2"):
                console.print("\n[bold cyan]:: VALUE-AWARE BEST-FIRST FUND TRACER ::[/bold cyan]")
                ident = input(" Enter Target Wallet Address or TXID: ").strip()
                if ident:
                    hops = input(" Enter Maximum Search Hops [default 8]: ").strip()
                    hops_val = int(hops) if hops.isdigit() else 8
                    self.msf.do_trace(f"{ident} {hops_val}")

            elif choice in ("03", "3"):
                console.print("\n[bold cyan]:: DIGITAL FORENSICS INVESTIGATOR ::[/bold cyan]")
                ident = input(" Enter TXID Hash, Wallet Address, or Relay IP: ").strip()
                if ident:
                    self.msf.do_investigate(ident)

            elif choice in ("04", "4"):
                console.print("\n[bold cyan]:: RANKED ALERT QUEUE ::[/bold cyan]")
                sev = input(" Filter Severity (CRITICAL/HIGH/MEDIUM or Enter for all): ").strip().upper()
                self.msf.do_show(f"alerts {sev}")
                dossier_id = input("\n Inspect Alert Dossier ID (or Enter to skip): ").strip()
                if dossier_id:
                    self.msf.do_explain(dossier_id)

            elif choice in ("05", "5"):
                console.print("\n[bold cyan]:: INFERRED ENTITY CLUSTERS ::[/bold cyan]")
                self.msf.do_show("entities")

            elif choice in ("06", "6"):
                console.print("\n[bold cyan]:: EXPLAINABILITY STUDIO (SHAP & COUNTERFACTUALS) ::[/bold cyan]")
                aid = input(" Enter Alert ID (e.g. ALT-1234): ").strip()
                if aid:
                    self.msf.do_explain(aid)

            elif choice in ("07", "7"):
                console.print("\n[bold cyan]:: SYNTHETIC ADVERSARIAL SCENARIOS ::[/bold cyan]")
                self.msf.do_show("scenarios")
                stype = input("\n Enter Scenario ID to Generate [default PEELING_CHAIN]: ").strip().upper() or "PEELING_CHAIN"
                count = input(" Transaction Count [default 15]: ").strip() or "15"
                self.msf.do_scenario(f"{stype} {count}")

            elif choice in ("08", "8"):
                console.print("\n[bold cyan]:: MACHINE LEARNING BENCHMARKS & EVALUATION ::[/bold cyan]")
                self.msf.do_show("models")

            elif choice in ("09", "9"):
                console.print("\n[bold cyan]:: INGEST TRANSACTION DATASET ::[/bold cyan]")
                fpath = input(" Enter Path to CSV, JSON, or XML file: ").strip()
                if fpath:
                    self.msf.do_ingest(fpath)

            elif choice in ("10"):
                console.print("\n[bold cyan]:: LOAD BUNDLED FORENSIC SAMPLE DATASET ::[/bold cyan]")
                self.msf.do_ingest("sample")

            elif choice in ("11"):
                console.print("\n[bold cyan]:: LAUNCH WEB COMMAND CENTER ::[/bold cyan]")
                port_str = input(" Enter Port [default 8000]: ").strip() or "8000"
                self.msf.do_serve(f"--port {port_str}")

            elif choice in ("12"):
                console.print("\n[bold cyan][*] Switching to MSF-Style Interactive Console Shell...[/bold cyan]")
                print_msf_header()
                self.msf.update_prompt()
                self.msf.cmdloop()
                break

            else:
                console.print(f"[bold red][-] Invalid selection '{choice}'. Please pick 00-12.[/bold red]")

            input("\n\033[2m[+] Press Enter to return to menu...\033[0m")
            os.system("clear" if os.name != "nt" else "cls")



# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

def main():
    """Main CLI dispatch."""
    args = sys.argv[1:]

    # Check flag for menu mode
    if "--menu" in args or "-m" in args:
        wizard = NexusZphisherMenu()
        wizard.run()
        return

    # Check for direct command invocation (e.g. `nexus-console trace <txid>`)
    if args and not args[0].startswith("-"):
        console_app = NexusMSFConsole()
        line = " ".join(args)
        console_app.onecmd(line)
        return

    # Default: Metasploit-style interactive console
    print_msf_header()
    app = NexusMSFConsole()
    app.update_prompt()
    try:
        app.cmdloop()
    except KeyboardInterrupt:
        console.print("\n[bold cyan][*] Console terminated by operator. Goodbye![/bold cyan]")


if __name__ == "__main__":
    main()
