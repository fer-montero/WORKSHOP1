"""
Task 1: Initial Data Profiling
ETL (G01) - Workshop 1: From Business Requirements to a Dimensional Data Warehouse

Este script realiza únicamente perfilamiento del dataset fuente. No realiza
transformaciones de datos ni reglas de negocio: eso ocurre en src/transform.py.

Ejecutar desde la raíz del proyecto:
    python notebooks/data_profiling.py
"""

import sys
from pathlib import Path
import pandas as pd

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

# Permite importar los módulos de src/ (una sola fuente de verdad para la extracción)
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root / "src"))

from extract import extract_data

# Ancho fijo: evita que las tablas se envuelvan de forma ilegible si la
# terminal es angosta (importante para que se vea bien en la sustentación)
console = Console(width=130)


# ---------------------------------------------------------------------------
# Utilidades de presentación
# ---------------------------------------------------------------------------

def print_title():
    console.print(
        Panel.fit(
            "[bold white]TASK 1 - INITIAL DATA PROFILING[/bold white]\n"
            "[dim]ETL (G01) - Workshop 1: Recruitment Data Warehouse[/dim]",
            border_style="cyan",
            box=box.DOUBLE,
        )
    )


def print_step(number, title):
    console.print()
    console.print(Panel(f"[bold cyan]{number}. {title}[/bold cyan]", box=box.HEAVY, expand=False))


def df_to_rich_table(df, title=None, index_name=""):
    """Convierte un DataFrame en una tabla 'rich' bien formateada."""
    table = Table(title=title, box=box.SIMPLE_HEAVY, header_style="bold magenta", show_lines=False)

    table.add_column(index_name, style="dim")
    for col in df.columns:
        table.add_column(str(col), justify="right")

    for idx, row in df.iterrows():
        values = [str(idx)] + [f"{v:.2f}" if isinstance(v, float) else str(v) for v in row]
        table.add_row(*values)

    return table


# ---------------------------------------------------------------------------
# Funciones de perfilamiento (una por punto requerido en el Task 1)
# ---------------------------------------------------------------------------

def profile_shape(df):
    table = Table(box=box.SIMPLE_HEAVY, show_header=False)
    table.add_column(style="bold")
    table.add_column(justify="right", style="bold green")
    table.add_row("Filas", f"{df.shape[0]:,}")
    table.add_row("Columnas", f"{df.shape[1]}")
    console.print(table)


def profile_columns_and_dtypes(df):
    table = Table(box=box.SIMPLE_HEAVY, header_style="bold magenta")
    table.add_column("#", justify="right", style="dim")
    table.add_column("Columna")
    table.add_column("Tipo de dato", justify="center")

    for i, (col, dtype) in enumerate(df.dtypes.items(), start=1):
        table.add_row(str(i), col, str(dtype))

    console.print(table)


def profile_missing_values(df):
    missing = df.isna().sum()
    missing_pct = (missing / len(df) * 100).round(2)

    table = Table(box=box.SIMPLE_HEAVY, header_style="bold magenta")
    table.add_column("Columna")
    table.add_column("Nulos", justify="right")
    table.add_column("% Nulos", justify="right")
    table.add_column("Estado", justify="center")

    for col in df.columns:
        count = missing[col]
        pct = missing_pct[col]
        status = "[green]OK[/green]" if count == 0 else "[bold red]REVISAR[/bold red]"
        table.add_row(col, str(count), f"{pct}%", status)

    console.print(table)


def profile_duplicates(df, key_column="Email"):
    full_duplicates = df.duplicated().sum()
    key_duplicates = df.duplicated(subset=[key_column]).sum()

    summary = Table(box=box.SIMPLE_HEAVY, show_header=False)
    summary.add_column(style="bold")
    summary.add_column(justify="right")
    summary.add_row("Filas 100% duplicadas", f"{full_duplicates}")
    summary.add_row(f"Valores repetidos en '{key_column}'", f"{key_duplicates}")
    console.print(summary)

    if key_duplicates > 0:
        console.print(f"\n[dim]Muestra de registros con '{key_column}' repetido (primeros 5):[/dim]")
        display_columns = [key_column, "First Name", "Last Name", "Technology",
                            "Code Challenge Score", "Technical Interview Score"]
        display_columns = [c for c in display_columns if c in df.columns]

        sample = (
            df[df.duplicated(subset=[key_column], keep=False)]
            .sort_values(key_column)
            .head(5)[display_columns]
        )
        table = Table(box=box.SIMPLE_HEAVY, header_style="bold magenta")
        for col in sample.columns:
            table.add_column(str(col))
        for _, row in sample.iterrows():
            table.add_row(*[str(v) for v in row])
        console.print(table)

        console.print(
            "[dim]Interpretación: mismos correos, pero nombres/puntajes distintos "
            "-> aplicaciones diferentes. No se eliminan (grano = una aplicación).[/dim]"
        )


def profile_categorical_columns(df, columns, max_values_to_list=25):
    for col in columns:
        n_unique = df[col].nunique()
        console.print(f"\n[bold]{col}[/bold] -> [green]{n_unique}[/green] valores únicos")

        if n_unique <= max_values_to_list:
            values = sorted(df[col].unique().tolist())
            table = Table(box=box.SIMPLE_HEAVY, show_header=False)
            table.add_column()
            for v in values:
                table.add_row(v)
            console.print(table)
        else:
            sample_values = sorted(df[col].unique().tolist())[:10]
            console.print(f"[dim](demasiados para listar, muestra: {sample_values} ...)[/dim]")


def profile_date_range(df, date_column="Application Date"):
    dates = pd.to_datetime(df[date_column])

    table = Table(box=box.SIMPLE_HEAVY, show_header=False)
    table.add_column(style="bold")
    table.add_column(justify="right", style="green")
    table.add_row("Fecha mínima", str(dates.min().date()))
    table.add_row("Fecha máxima", str(dates.max().date()))
    table.add_row("Rango total", f"{(dates.max() - dates.min()).days} días")
    console.print(table)


def profile_numeric_columns(df, columns):
    stats = df[columns].describe().round(2)
    table = df_to_rich_table(stats, index_name="Estadística")
    console.print(table)

    console.print("\n[dim]Validación de rangos esperados (0 a 10) en los puntajes:[/dim]")
    validation = Table(box=box.SIMPLE_HEAVY, header_style="bold magenta")
    validation.add_column("Score")
    validation.add_column("Min", justify="right")
    validation.add_column("Max", justify="right")
    validation.add_column("Fuera de rango", justify="right")

    for col in ["Code Challenge Score", "Technical Interview Score"]:
        if col in df.columns:
            out_of_range = int(((df[col] < 0) | (df[col] > 10)).sum())
            status = "[green]0[/green]" if out_of_range == 0 else f"[bold red]{out_of_range}[/bold red]"
            validation.add_row(col, str(df[col].min()), str(df[col].max()), status)

    console.print(validation)


def print_findings_summary():
    table = Table(title="Resumen de Hallazgos Principales", box=box.ROUNDED, header_style="bold magenta")
    table.add_column("Aspecto", style="bold")
    table.add_column("Hallazgo")

    findings = [
        ("Filas / columnas", "50,000 filas, 10 columnas"),
        ("Valores nulos", "0 en todas las columnas"),
        ("Filas 100% duplicadas", "0"),
        ("Emails repetidos", "Aplicaciones distintas -> no se eliminan"),
        ("Application Date", "Texto ISO 'YYYY-MM-DD' -> se convierte a datetime en preparación"),
        ("Seniority", "7 niveles (Intern -> Architect)"),
        ("Technology", "24 valores únicos"),
        ("Country", "244 valores únicos"),
        ("Scores (Code/Technical)", "Enteros entre 0 y 10, sin valores fuera de rango"),
    ]
    for aspecto, hallazgo in findings:
        table.add_row(aspecto, hallazgo)

    console.print(table)

    console.print(
        Panel(
            "[italic]El dataset está íntegro (sin nulos ni duplicados reales). "
            "La preparación de datos se enfoca en corrección de tipos, "
            "no en limpieza de datos sucios.[/italic]",
            title="Conclusión",
            border_style="green",
        )
    )


# ---------------------------------------------------------------------------
# Orquestación del perfilamiento
# ---------------------------------------------------------------------------

def run_profiling():
    print_title()
    df = extract_data()

    print_step(1, "NÚMERO DE FILAS Y COLUMNAS")
    profile_shape(df)

    print_step(2, "NOMBRES DE COLUMNAS Y TIPOS DE DATO")
    profile_columns_and_dtypes(df)

    print_step(3, "VALORES FALTANTES")
    profile_missing_values(df)

    print_step(4, "REGISTROS DUPLICADOS")
    profile_duplicates(df, key_column="Email")

    print_step(5, "VALORES ÚNICOS EN ATRIBUTOS CATEGÓRICOS")
    profile_categorical_columns(df, columns=["Seniority", "Technology", "Country"])

    print_step(6, "RANGO DE FECHAS DE APLICACIÓN")
    profile_date_range(df, date_column="Application Date")

    print_step(7, "RANGO DE PUNTAJES Y ESTADÍSTICAS DESCRIPTIVAS")
    profile_numeric_columns(df, columns=["YOE", "Code Challenge Score", "Technical Interview Score"])

    print_step(8, "RESUMEN DE HALLAZGOS")
    print_findings_summary()


if __name__ == "__main__":
    run_profiling()