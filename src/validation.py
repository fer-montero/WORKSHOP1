"""
Data Quality Validations - previas a la carga al Data Warehouse.

Este módulo NO está explícitamente pedido como archivo separado en el
enunciado del taller, pero implementa (de forma anticipada, en Python)
las mismas verificaciones que la Tarea 5 exige validar tras la carga:
    - Claves primarias.
    - Claves externas.
    - Integridad referencial.
    - Número de registros cargados.
    - Ausencia de referencias de dimensión no válidas.

Validar aquí, antes de tocar la base de datos, evita cargar datos
corruptos al Data Warehouse y facilita depurar errores en Python en
vez de en SQL.
"""

import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console(width=130)


class ValidationError(Exception):
    """Se lanza cuando el Star Schema no pasa una validación crítica."""
    pass


# ---------------------------------------------------------------------------
# Validaciones individuales
# ---------------------------------------------------------------------------

def validate_primary_keys(star_schema):
    """
    Verifica que la clave primaria (surrogate key) de cada dimensión y de
    la tabla de hechos sea única y no tenga nulos.
    """
    pk_by_table = {
        "dim_date": "date_key",
        "dim_candidate": "candidate_key",
        "dim_technology": "technology_key",
        "dim_country": "country_key",
        "fact_application": "application_key",
    }

    results = []
    for table_name, pk_column in pk_by_table.items():
        table = star_schema[table_name]

        has_nulls = table[pk_column].isna().any()
        is_unique = table[pk_column].is_unique

        results.append({
            "table": table_name,
            "primary_key": pk_column,
            "rows": len(table),
            "nulls": int(table[pk_column].isna().sum()),
            "unique": is_unique,
            "passed": (not has_nulls) and is_unique,
        })

    return results


def validate_foreign_keys(star_schema):
    """
    Verifica integridad referencial: cada FK en FACT_APPLICATION debe
    existir dentro de la PK de su dimensión correspondiente. Esto detecta
    "referencias de dimensión no válidas" en Python, antes de cargar.
    """
    fact = star_schema["fact_application"]

    fk_to_dim = {
        "date_key": ("dim_date", "date_key"),
        "candidate_key": ("dim_candidate", "candidate_key"),
        "technology_key": ("dim_technology", "technology_key"),
        "country_key": ("dim_country", "country_key"),
    }

    results = []
    for fk_column, (dim_name, dim_key) in fk_to_dim.items():
        valid_keys = set(star_schema[dim_name][dim_key])
        fact_keys = set(fact[fk_column].dropna())

        orphan_keys = fact_keys - valid_keys
        null_count = int(fact[fk_column].isna().sum())

        results.append({
            "foreign_key": fk_column,
            "references": f"{dim_name}.{dim_key}",
            "nulls": null_count,
            "orphan_values": len(orphan_keys),
            "passed": (null_count == 0) and (len(orphan_keys) == 0),
        })

    return results


def validate_row_counts(df_source, star_schema):
    """
    Verifica que el número de hechos cargados coincida exactamente con el
    número de aplicaciones de origen: no se perdieron ni se duplicaron
    aplicaciones durante la transformación dimensional.
    """
    expected = len(df_source)
    actual = len(star_schema["fact_application"])

    return {
        "expected_rows": expected,
        "actual_rows": actual,
        "passed": expected == actual,
    }


def validate_measure_ranges(star_schema):
    """
    Verifica que las medidas de FACT_APPLICATION estén dentro de rangos
    de negocio válidos (defensivo: detecta errores de mapeo o de la
    regla de negocio antes de cargarlos a la base de datos).
    """
    fact = star_schema["fact_application"]

    checks = [
        {
            "measure": "code_score",
            "rule": "entre 0 y 10",
            "passed": fact["code_score"].between(0, 10).all(),
        },
        {
            "measure": "interview_score",
            "rule": "entre 0 y 10",
            "passed": fact["interview_score"].between(0, 10).all(),
        },
        {
            "measure": "hired_indicator",
            "rule": "solo valores 0 o 1",
            "passed": fact["hired_indicator"].isin([0, 1]).all(),
        },
    ]
    return checks


# ---------------------------------------------------------------------------
# Orquestación: ejecuta todas las validaciones y decide si se puede cargar
# ---------------------------------------------------------------------------

def run_all_validations(df_source, star_schema):
    """
    Ejecuta todas las validaciones sobre el Star Schema ya construido.

    Returns
    -------
    dict
        Reporte completo con los resultados de cada validación.

    Raises
    ------
    ValidationError
        Si alguna validación crítica falla (no se debe continuar hacia
        la carga en el Data Warehouse).
    """
    report = {
        "primary_keys": validate_primary_keys(star_schema),
        "foreign_keys": validate_foreign_keys(star_schema),
        "row_counts": validate_row_counts(df_source, star_schema),
        "measure_ranges": validate_measure_ranges(star_schema),
    }

    failures = []
    failures += [r for r in report["primary_keys"] if not r["passed"]]
    failures += [r for r in report["foreign_keys"] if not r["passed"]]
    if not report["row_counts"]["passed"]:
        failures.append(report["row_counts"])
    failures += [r for r in report["measure_ranges"] if not r["passed"]]

    report["all_passed"] = len(failures) == 0
    report["failures"] = failures

    if not report["all_passed"]:
        raise ValidationError(
            f"El Star Schema no pasó {len(failures)} validación(es). "
            f"Revisa el reporte antes de continuar a la carga."
        )

    return report


# ---------------------------------------------------------------------------
# Reporte visual (rich) — para consola / sustentación
# ---------------------------------------------------------------------------

def report_validations(report):
    """Imprime el resultado de las validaciones de forma clara y visual."""

    # --- Claves primarias ---
    pk_table = Table(title="Claves Primarias (Surrogate Keys)", box=box.SIMPLE_HEAVY, header_style="bold magenta")
    pk_table.add_column("Tabla")
    pk_table.add_column("PK")
    pk_table.add_column("Filas", justify="right")
    pk_table.add_column("Nulos", justify="right")
    pk_table.add_column("Única", justify="center")
    pk_table.add_column("Estado", justify="center")

    for r in report["primary_keys"]:
        status = "[green]OK[/green]" if r["passed"] else "[bold red]FALLA[/bold red]"
        pk_table.add_row(
            r["table"], r["primary_key"], f"{r['rows']:,}",
            str(r["nulls"]), str(r["unique"]), status,
        )
    console.print(pk_table)

    # --- Claves foráneas / integridad referencial ---
    fk_table = Table(title="Integridad Referencial (Foreign Keys)", box=box.SIMPLE_HEAVY, header_style="bold magenta")
    fk_table.add_column("FK en fact_application")
    fk_table.add_column("Referencia")
    fk_table.add_column("Nulos", justify="right")
    fk_table.add_column("Valores huérfanos", justify="right")
    fk_table.add_column("Estado", justify="center")

    for r in report["foreign_keys"]:
        status = "[green]OK[/green]" if r["passed"] else "[bold red]FALLA[/bold red]"
        fk_table.add_row(
            r["foreign_key"], r["references"],
            str(r["nulls"]), str(r["orphan_values"]), status,
        )
    console.print(fk_table)

    # --- Conteo de registros ---
    rc = report["row_counts"]
    status = "[green]OK[/green]" if rc["passed"] else "[bold red]FALLA[/bold red]"
    console.print(
        f"\n[bold]Conteo de registros:[/bold] esperados={rc['expected_rows']:,}  "
        f"actuales={rc['actual_rows']:,}  {status}"
    )

    # --- Rangos de medidas ---
    measure_table = Table(title="Rangos de Medidas", box=box.SIMPLE_HEAVY, header_style="bold magenta")
    measure_table.add_column("Medida")
    measure_table.add_column("Regla esperada")
    measure_table.add_column("Estado", justify="center")

    for r in report["measure_ranges"]:
        status = "[green]OK[/green]" if r["passed"] else "[bold red]FALLA[/bold red]"
        measure_table.add_row(r["measure"], r["rule"], status)
    console.print(measure_table)

    # --- Veredicto final ---
    if report["all_passed"]:
        console.print(
            Panel(
                "[bold green]Todas las validaciones pasaron correctamente.\n"
                "El Star Schema está listo para cargarse al Data Warehouse.[/bold green]",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel(
                f"[bold red]{len(report['failures'])} validación(es) fallaron.\n"
                f"NO continúes con la carga hasta corregir esto.[/bold red]",
                border_style="red",
            )
        )