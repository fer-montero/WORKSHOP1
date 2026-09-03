"""
load.py — Carga del Star Schema al Data Warehouse (MySQL).

Orden obligatorio de carga: Dimensiones -> Fact Table.
Después de cargar, se valida directamente contra la base de datos:
    - Conteo de filas por tabla.
    - Integridad referencial (FKs sin huérfanos).
    - Ausencia de referencias de dimensión inválidas.
"""

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

load_dotenv()
console = Console(width=130)


# ---------------------------------------------------------------------------
# Conexión
# ---------------------------------------------------------------------------

def get_engine():
    """Crea el engine de SQLAlchemy hacia MySQL usando variables de entorno."""
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME")

    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"
    return create_engine(url)


# ---------------------------------------------------------------------------
# Creación del esquema
# ---------------------------------------------------------------------------

def create_schema(engine, sql_path="sql/create_tables.sql"):
    """Ejecuta el DDL que crea (o recrea) las tablas del Data Warehouse."""
    script = Path(sql_path).read_text(encoding="utf-8")

    # MySQL no ejecuta varios statements en una sola llamada por defecto,
    # así que los separamos por ';' y ejecutamos uno a uno.
    statements = [s.strip() for s in script.split(";") if s.strip()]

    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))


# ---------------------------------------------------------------------------
# Carga de tablas
# ---------------------------------------------------------------------------

# Mapeo: nombre lógico en star_schema -> nombre real de tabla en MySQL
TABLE_NAME_MAP = {
    "dim_date": "dim_date",
    "dim_candidate": "dim_candidate",
    "dim_technology": "dim_technology",
    "dim_country": "dim_country",
    "fact_application": "fact_application",
}

# Orden de carga: dimensiones primero, hechos al final
LOAD_ORDER = [
    "dim_date",
    "dim_candidate",
    "dim_technology",
    "dim_country",
    "fact_application",
]


def load_dataframe(engine, df, table_name):
    """Inserta un DataFrame en una tabla existente (append, sin tocar el DDL)."""
    df.to_sql(table_name, con=engine, if_exists="append", index=False)


def load_star_schema(engine, star_schema):
    """
    Carga todas las tablas del star schema en el orden correcto:
    dimensiones -> tabla de hechos.
    """
    for table_key in LOAD_ORDER:
        df = star_schema[table_key]
        table_name = TABLE_NAME_MAP[table_key]
        load_dataframe(engine, df, table_name)
        console.print(f"[green]OK[/green] Cargada tabla [bold]{table_name}[/bold] ({len(df):,} filas)")


# ---------------------------------------------------------------------------
# Validación POST-carga (contra la base de datos real)
# ---------------------------------------------------------------------------

def validate_row_counts(engine, star_schema):
    """Compara filas en cada DataFrame vs. filas realmente cargadas en MySQL."""
    results = []
    for table_key, table_name in TABLE_NAME_MAP.items():
        expected = len(star_schema[table_key])
        with engine.connect() as conn:
            actual = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
        results.append({
            "table": table_name,
            "expected": expected,
            "actual": actual,
            "passed": expected == actual,
        })
    return results


def validate_referential_integrity(engine):
    """
    Verifica, directamente en MySQL, que no existan claves foráneas
    huérfanas en fact_application (referencias a dimensiones inválidas).
    Como las FKs ya están declaradas en el DDL, en teoría MySQL nunca
    dejaría insertar un huérfano — esta consulta es una doble verificación
    explícita, tal como lo pide el enunciado.
    """
    checks = {
        "date_key": "dim_date",
        "candidate_key": "dim_candidate",
        "technology_key": "dim_technology",
        "country_key": "dim_country",
    }

    results = []
    with engine.connect() as conn:
        for fk_column, dim_table in checks.items():
            dim_key = fk_column  # mismo nombre de columna en la dimensión
            query = text(f"""
                SELECT COUNT(*) 
                FROM fact_application f
                LEFT JOIN {dim_table} d ON f.{fk_column} = d.{dim_key}
                WHERE d.{dim_key} IS NULL
            """)
            orphan_count = conn.execute(query).scalar()
            results.append({
                "foreign_key": fk_column,
                "references": f"{dim_table}.{dim_key}",
                "orphan_rows": orphan_count,
                "passed": orphan_count == 0,
            })
    return results


def validate_primary_keys(engine):
    """Verifica unicidad y no-nulidad de las PKs directamente en MySQL."""
    pk_by_table = {
        "dim_date": "date_key",
        "dim_candidate": "candidate_key",
        "dim_technology": "technology_key",
        "dim_country": "country_key",
        "fact_application": "application_key",
    }

    results = []
    with engine.connect() as conn:
        for table_name, pk_column in pk_by_table.items():
            total = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            distinct = conn.execute(text(f"SELECT COUNT(DISTINCT {pk_column}) FROM {table_name}")).scalar()
            nulls = conn.execute(text(f"SELECT COUNT(*) FROM {table_name} WHERE {pk_column} IS NULL")).scalar()
            results.append({
                "table": table_name,
                "primary_key": pk_column,
                "rows": total,
                "unique": total == distinct,
                "nulls": nulls,
                "passed": (total == distinct) and (nulls == 0),
            })
    return results


def report_load_validation(pk_results, fk_results, count_results):
    """Imprime el reporte visual de validación post-carga."""

    pk_table = Table(title="Claves Primarias en MySQL", box=box.SIMPLE_HEAVY, header_style="bold magenta")
    pk_table.add_column("Tabla")
    pk_table.add_column("PK")
    pk_table.add_column("Filas", justify="right")
    pk_table.add_column("Única", justify="center")
    pk_table.add_column("Nulos", justify="right")
    pk_table.add_column("Estado", justify="center")
    for r in pk_results:
        status = "[green]OK[/green]" if r["passed"] else "[bold red]FALLA[/bold red]"
        pk_table.add_row(r["table"], r["primary_key"], f"{r['rows']:,}", str(r["unique"]), str(r["nulls"]), status)
    console.print(pk_table)

    fk_table = Table(title="Integridad Referencial en MySQL", box=box.SIMPLE_HEAVY, header_style="bold magenta")
    fk_table.add_column("FK")
    fk_table.add_column("Referencia")
    fk_table.add_column("Filas huérfanas", justify="right")
    fk_table.add_column("Estado", justify="center")
    for r in fk_results:
        status = "[green]OK[/green]" if r["passed"] else "[bold red]FALLA[/bold red]"
        fk_table.add_row(r["foreign_key"], r["references"], str(r["orphan_rows"]), status)
    console.print(fk_table)

    count_table = Table(title="Conteo de Registros Cargados", box=box.SIMPLE_HEAVY, header_style="bold magenta")
    count_table.add_column("Tabla")
    count_table.add_column("Esperados", justify="right")
    count_table.add_column("Cargados", justify="right")
    count_table.add_column("Estado", justify="center")
    for r in count_results:
        status = "[green]OK[/green]" if r["passed"] else "[bold red]FALLA[/bold red]"
        count_table.add_row(r["table"], f"{r['expected']:,}", f"{r['actual']:,}", status)
    console.print(count_table)

    all_passed = all(r["passed"] for r in pk_results + fk_results + count_results)
    if all_passed:
        console.print(Panel("[bold green]Carga validada correctamente en MySQL.[/bold green]", border_style="green"))
    else:
        console.print(Panel("[bold red]La carga tiene inconsistencias. Revisa el reporte.[/bold red]", border_style="red"))

    return all_passed