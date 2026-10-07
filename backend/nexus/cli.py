"""NEXUS-BTC CLI Command Line Interface."""

import sys
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table

# Ensure backend root is on sys.path
backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.core.config import settings
from app.ingestion.engine import IngestionEngine
from app.services.pipeline import ForensicPipeline
from app.services.scenario_generator import ScenarioGenerator
from app.schemas.scenario import ScenarioGenerateRequest

console = Console()


@click.group()
def cli():
    """NEXUS-BTC: Network–Entity eXplainable Unified Surveillance for Bitcoin."""
    pass


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--analyze/--no-analyze", default=True, help="Trigger forensic pipeline after ingest.")
def ingest(file_path: str, analyze: bool):
    """Ingest a CSV, JSON, or XML transaction file into local forensics database."""
    console.print(f"[bold cyan]NEXUS-BTC Ingestion Engine[/bold cyan] reading: [yellow]{file_path}[/yellow]")
    engine = IngestionEngine()

    try:
        result = engine.ingest_file(Path(file_path))

        table = Table(title="Ingestion Execution Report", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="dim")
        table.add_column("Value", justify="right")

        table.add_row("Ingestion ID", result.ingestion_id[:12] + "...")
        table.add_row("Source File", Path(result.source_file).name)
        table.add_row("Records Read", str(result.records_read))
        table.add_row("Records Valid", f"[green]{result.records_valid}[/green]")
        table.add_row("Records Quarantined", f"[red]{result.records_invalid}[/red]")
        table.add_row("Duplicates Filtered", str(result.duplicates))
        table.add_row("Normalization Warnings", str(result.normalization_warnings))
        table.add_row("Execution Time", f"{result.execution_time_seconds:.3f}s")
        table.add_row("Status", f"[bold green]{result.status}[/bold green]")

        console.print(table)

        if analyze and result.records_valid > 0:
            console.print("\n[bold cyan]Triggering Automated Forensic Pipeline...[/bold cyan]")
            pipeline = ForensicPipeline()
            summary = pipeline.run_full_pipeline()
            console.print(f"[green]✓ Analysis complete: {summary.get('alerts_generated', 0)} alerts generated "
                          f"({summary.get('critical_alerts', 0)} CRITICAL, "
                          f"{summary.get('high_alerts', 0)} HIGH)[/green]")

    except Exception as e:
        console.print(f"[bold red]Ingestion Error:[/bold red] {e}")
        sys.exit(1)


@cli.command()
def pipeline():
    """Run full forensic pipeline across all stored transactions."""
    console.print("[bold cyan]Running NEXUS-BTC Master Pipeline...[/bold cyan]")
    p = ForensicPipeline()
    summary = p.run_full_pipeline()
    console.print(f"[bold green]✓ Pipeline finished in {summary.get('execution_time_seconds', 0)}s[/bold green]")
    console.print(f"  • Transactions: {summary.get('transactions_analyzed', 0)}")
    console.print(f"  • Entities:     {summary.get('entities_clustered', 0)}")
    console.print(f"  • Alerts:       {summary.get('alerts_generated', 0)} ({summary.get('critical_alerts', 0)} critical)")


@cli.command()
@click.option("--host", default="127.0.0.1", help="Bind host.")
@click.option("--port", default=8000, help="Bind port.")
def serve(host: str, port: int):
    """Start local offline FastAPI backend web server."""
    import uvicorn
    console.print(f"[bold green]Starting NEXUS-BTC local server on http://{host}:{port}[/bold green]")
    uvicorn.run("app.main:app", host=host, port=port, reload=False)


@cli.command()
@click.argument("scenario_type", default="PEELING_CHAIN")
def scenario(scenario_type: str):
    """Generate a synthetic forensic adversarial scenario."""
    gen = ScenarioGenerator()
    req = ScenarioGenerateRequest(scenario_type=scenario_type.upper())
    resp, _ = gen.generate(req)
    console.print(f"[green]✓ Generated {resp.record_count} records for scenario {scenario_type}[/green]")
    console.print(f"  Saved to: {resp.output_filepath}")


@cli.command(name="console")
def console_cmd():

    """Launch Metasploit-style interactive forensic console shell (nexus-btc > )."""
    from nexus.console import print_msf_header, NexusMSFConsole
    print_msf_header()
    app = NexusMSFConsole()
    app.update_prompt()
    try:
        app.cmdloop()
    except KeyboardInterrupt:
        console.print("\n[bold cyan][*] Exiting NEXUS-BTC console.[/bold cyan]")


@cli.command()
def menu():
    """Launch Zphisher-style numbered wizard menu."""
    from nexus.console import NexusZphisherMenu
    wizard = NexusZphisherMenu()
    wizard.run()


@cli.command()
@click.argument("identifier")
@click.option("--hops", default=8, help="Maximum search hops.")
@click.option("--type", "ident_type", default="wallet", type=click.Choice(["wallet", "txid", "entity"]))
def trace(identifier: str, hops: int, ident_type: str):
    """Execute Value-Aware Best-First Fund Tracer on a wallet or TXID."""
    from nexus.console import NexusMSFConsole
    c = NexusMSFConsole()
    c.do_trace(f"{identifier} {hops} {ident_type}")


@cli.command()
@click.argument("identifier")
def investigate(identifier: str):
    """Deep forensic transaction & relay telemetry inspection."""
    from nexus.console import NexusMSFConsole
    c = NexusMSFConsole()
    c.do_investigate(identifier)


@cli.command()
@click.argument("alert_id")
def explain(alert_id: str):
    """Display SHAP feature waterfall & counterfactual sensitivity analysis."""
    from nexus.console import NexusMSFConsole
    c = NexusMSFConsole()
    c.do_explain(alert_id)

