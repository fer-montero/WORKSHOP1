from extract import extract_data
from transform import prepare_data, apply_business_rules
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from dimensional_model import build_star_schema
from validation import run_all_validations, report_validations, ValidationError
from load import get_engine, create_schema, load_star_schema, \
    validate_primary_keys, validate_referential_integrity, validate_row_counts, \
    report_load_validation

console = Console(width=130)


def print_section(title):
    console.print()
    console.print(Panel(f"[bold cyan]{title}[/bold cyan]", box=box.HEAVY, expand=False))


def report_extraction(df):
    table = Table(box=box.SIMPLE_HEAVY, show_header=False)
    table.add_column(style="bold")
    table.add_column(justify="right", style="bold green")
    table.add_row("Registros extraídos", f"{len(df):,}")
    table.add_row("Columnas extraídas", f"{len(df.columns)}")
    console.print(table)


def report_preparation(df):
    table = Table(box=box.SIMPLE_HEAVY, header_style="bold magenta")
    table.add_column("Columna")
    table.add_column("Tipo de dato", justify="center")
    for col, dtype in df.dtypes.items():
        table.add_row(col, str(dtype))
    console.print(table)

    console.print(f"\n[dim]Rango de fechas: {df['Application Date'].min().date()} a {df['Application Date'].max().date()}[/dim]")


def report_business_rules(df):
    total = len(df)
    hired = int(df["Hired"].sum())
    not_hired = total - hired
    hired_pct = round(hired / total * 100, 2)

    table = Table(box=box.SIMPLE_HEAVY, show_header=False)
    table.add_column(style="bold")
    table.add_column(justify="right")
    table.add_row("Total aplicaciones", f"{total:,}")
    table.add_row("[green]HIRED[/green]", f"{hired:,} ({hired_pct}%)")
    table.add_row("[red]NOT HIRED[/red]", f"{not_hired:,} ({100 - hired_pct}%)")
    console.print(table)

    console.print("\n[dim]Muestra de resultado (primeras 5 filas):[/dim]")
    sample_cols = ["First Name", "Last Name", "Code Challenge Score", "Technical Interview Score", "Hired"]
    sample = df[sample_cols].head()
    sample_table = Table(box=box.SIMPLE_HEAVY, header_style="bold magenta")
    for col in sample.columns:
        sample_table.add_column(col)
    for _, row in sample.iterrows():
        sample_table.add_row(*[str(v) for v in row])
    console.print(sample_table)


def main():
    print_section("INICIO DEL PROCESO ETL")

    # --- EXTRACCIÓN ---
    print_section("EXTRACCIÓN")
    df_raw = extract_data()
    report_extraction(df_raw)

    # --- PREPARACIÓN DE DATOS ---
    print_section("PREPARACIÓN DE DATOS")
    df_prepared = prepare_data(df_raw)
    report_preparation(df_prepared)

    # --- TRANSFORMACIÓN DE NEGOCIO ---
    print_section("TRANSFORMACIÓN DE NEGOCIO (regla HIRED)")
    df_transformed = apply_business_rules(df_prepared)
    report_business_rules(df_transformed)

    
    print_section("TRANSFORMACIÓN DIMENSIONAL (Star Schema)")
    star_schema = build_star_schema(df_transformed)

    for name, table in star_schema.items():
        print(f"{name}: {len(table):,} filas")

     # --- VALIDACIÓN DE CALIDAD DE DATOS (previa a la carga) ---
    print_section("VALIDACIÓN DE CALIDAD DE DATOS")
    try:
        report = run_all_validations(df_transformed, star_schema)
        report_validations(report)
    except ValidationError as e:
        report_validations(e.args[0] if isinstance(e.args[0], dict) else {})
        console.print(f"\n[bold red]Proceso detenido:[/bold red] {e}")
        return  # detiene el pipeline: no continúa hacia la carga

    # --- CARGA AL DATA WAREHOUSE (MySQL) ---
    print_section("CARGA AL DATA WAREHOUSE")
    engine = get_engine()
    create_schema(engine, sql_path="sql/create_tables.sql")
    load_star_schema(engine, star_schema)

    # --- VALIDACIÓN POST-CARGA (contra MySQL real) ---
    print_section("VALIDACIÓN POST-CARGA EN MYSQL")
    pk_results = validate_primary_keys(engine)
    fk_results = validate_referential_integrity(engine)
    count_results = validate_row_counts(engine, star_schema)
    load_ok = report_load_validation(pk_results, fk_results, count_results)

    if not load_ok:
        console.print("[bold red]Advertencia:[/bold red] la carga presenta inconsistencias.")

    print_section("FIN DEL PROCESO ETL")


if __name__ == "__main__":
    main()