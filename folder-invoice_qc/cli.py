import typer
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from .extractor import extract_invoice_from_pdf
from .validator import run_batch_validation

app = typer.Typer()
console = Console()

@app.command()
def extract(
    pdf_dir: Path = typer.Option(..., help="Directory containing PDF invoices"),
    output: Path = typer.Option(..., help="Path to save extracted JSON")
):
    if not pdf_dir.exists():
        console.print(f"[bold red]Error:[/bold red] Directory {pdf_dir} missing.")
        raise typer.Exit(code=1)

    extracted_data = []
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    with console.status(f"Extracting from {len(pdf_files)} files..."):
        for pdf_file in pdf_files:
            data = extract_invoice_from_pdf(str(pdf_file))
            if data:
                extracted_data.append(data)
            else:
                console.print(f"[yellow]Warning:[/yellow] Failed to parse {pdf_file.name}")

    with open(output, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, indent=2, default=str)
    console.print(f"[bold green]Success![/bold green] Extracted {len(extracted_data)} invoices.")

@app.command()
def validate(
    input_json: Path = typer.Option(..., help="Path to extracted JSON"),
    report: Path = typer.Option(..., help="Path to save report")
):
    if not input_json.exists():
        console.print(f"[bold red]Error:[/bold red] File {input_json} missing.")
        raise typer.Exit(code=1)

    with open(input_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    report_data = run_batch_validation(data)
    with open(report, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    summary = report_data["summary"]
    table = Table(title="Validation Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_row("Total Processed", str(summary["total_processed"]))
    table.add_row("Valid", str(summary["valid_invoices"]))
    table.add_row("Invalid", f"[red]{summary['invalid_invoices']}[/red]")
    console.print(table)
    
    if summary["invalid_invoices"] > 0:
        raise typer.Exit(code=1)

@app.command()
def full_run(
    pdf_dir: Path = typer.Option(..., help="PDF Directory"),
    report: Path = typer.Option("report.json", help="Report Path")
):
    extracted_data = []
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    console.print(f"[bold blue]Step 1: Extraction[/bold blue]")
    for pdf_file in pdf_files:
        data = extract_invoice_from_pdf(str(pdf_file))
        if data:
            extracted_data.append(data)
    
    console.print(f"[bold blue]Step 2: Validation[/bold blue]")
    report_data = run_batch_validation(extracted_data)
    
    with open(report, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, default=str)
        
    summary = report_data["summary"]
    console.print(f"Processed: {summary['total_processed']} | Valid: {summary['valid_invoices']} | Invalid: {summary['invalid_invoices']}")
    if summary["invalid_invoices"] > 0:
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
