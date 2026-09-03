"""
Task 4: Dimensional Transformation
ETL (G01) - Workshop 1: From Business Requirements to a Dimensional Data Warehouse

Transforma los datos de origen ya preparados (salida de transform.py) en las
estructuras del Star Schema definido en la Tarea 2:

    DIM_DATE, DIM_CANDIDATE, DIM_TECHNOLOGY, DIM_COUNTRY  ->  FACT_APPLICATION

Flujo conceptual:
    Datos preparados -> Registros de dimensiones -> Claves sustitutas
    -> Asignación de claves -> Tabla de hechos
"""

import pandas as pd


# ---------------------------------------------------------------------------
# Utilidad común: generación de claves sustitutas
# ---------------------------------------------------------------------------

def _add_surrogate_key(dim_df, key_name):
    """
    Genera una clave sustituta secuencial (1, 2, 3, ...) para una dimensión.

    Importante: NUNCA se usa la clave natural del origen (email, nombre de
    tecnología, fecha, etc.) como llave primaria. La clave sustituta es un
    entero independiente del significado del dato, tal como lo exige el
    profesor.
    """
    dim_df = dim_df.reset_index(drop=True).copy()
    dim_df.insert(0, key_name, range(1, len(dim_df) + 1))
    return dim_df


# ---------------------------------------------------------------------------
# 1. Construcción de las dimensiones
# ---------------------------------------------------------------------------

def build_dim_date(df):
    """
    Construye DIM_DATE a partir de las fechas únicas de aplicación.

    Se conserva 'full_date' como atributo (no como PK) para poder mapear
    cada aplicación a su date_key correspondiente más adelante.
    """
    dim_date = df[["Application Date"]].drop_duplicates()
    dim_date = dim_date.rename(columns={"Application Date": "full_date"})
    dim_date = dim_date.sort_values("full_date")

    dim_date["day"] = dim_date["full_date"].dt.day
    dim_date["month"] = dim_date["full_date"].dt.month
    dim_date["quarter"] = dim_date["full_date"].dt.quarter
    dim_date["year"] = dim_date["full_date"].dt.year

    dim_date = _add_surrogate_key(dim_date, "date_key")
    return dim_date[["date_key", "full_date", "day", "month", "quarter", "year"]]


def build_dim_candidate(df):
    """
    Construye DIM_CANDIDATE a partir de los atributos del candidato.

    Se deduplican combinaciones exactas de (nombre, apellido, email, yoe,
    seniority). En este dataset no hay combinaciones repetidas (cada
    aplicación trae un perfil distinto), pero el proceso de deduplicación
    se deja implementado por si una carga futura sí las tuviera.
    """
    candidate_cols = ["First Name", "Last Name", "Email", "YOE", "Seniority"]
    dim_candidate = df[candidate_cols].drop_duplicates()
    dim_candidate = dim_candidate.rename(columns={
        "First Name": "first_name",
        "Last Name": "last_name",
        "Email": "email",
        "YOE": "yoe",
        "Seniority": "seniority",
    })
    dim_candidate = dim_candidate.sort_values(["last_name", "first_name"])

    dim_candidate = _add_surrogate_key(dim_candidate, "candidate_key")
    return dim_candidate[["candidate_key", "first_name", "last_name", "email", "yoe", "seniority"]]


def build_dim_technology(df):
    """Construye DIM_TECHNOLOGY a partir de las tecnologías únicas."""
    dim_technology = df[["Technology"]].drop_duplicates()
    dim_technology = dim_technology.rename(columns={"Technology": "technology"})
    dim_technology = dim_technology.sort_values("technology")

    dim_technology = _add_surrogate_key(dim_technology, "technology_key")
    return dim_technology[["technology_key", "technology"]]


def build_dim_country(df):
    """Construye DIM_COUNTRY a partir de los países únicos."""
    dim_country = df[["Country"]].drop_duplicates()
    dim_country = dim_country.rename(columns={"Country": "country"})
    dim_country = dim_country.sort_values("country")

    dim_country = _add_surrogate_key(dim_country, "country_key")
    return dim_country[["country_key", "country"]]


# ---------------------------------------------------------------------------
# 2. Construcción de la tabla de hechos
# ---------------------------------------------------------------------------

def build_fact_application(df, dim_date, dim_candidate, dim_technology, dim_country):
    """
    Construye FACT_APPLICATION según el grano declarado:
    "Una fila en FACT_APPLICATION representa una aplicación de un
    candidato a una tecnología en una fecha y país específicos."

    Cada aplicación se mapea a la clave sustituta correspondiente de cada
    dimensión mediante un merge por la clave natural (fecha, combinación de
    candidato, tecnología, país).
    """

    fact = df.copy()

    # --- Mapeo a claves sustitutas (una unión por dimensión) ---
    fact = fact.merge(
        dim_date[["date_key", "full_date"]],
        left_on="Application Date", right_on="full_date", how="left",
    )

    fact = fact.merge(
        dim_candidate[["candidate_key", "first_name", "last_name", "email", "yoe", "seniority"]],
        left_on=["First Name", "Last Name", "Email", "YOE", "Seniority"],
        right_on=["first_name", "last_name", "email", "yoe", "seniority"],
        how="left",
    )

    fact = fact.merge(
        dim_technology[["technology_key", "technology"]],
        left_on="Technology", right_on="technology", how="left",
    )

    fact = fact.merge(
        dim_country[["country_key", "country"]],
        left_on="Country", right_on="country", how="left",
    )

    # --- Validación de integridad referencial ---
    # Si alguna clave foránea quedó nula, significa que una aplicación no
    # encontró coincidencia en su dimensión: esto NO debe ocurrir.
    fk_columns = ["date_key", "candidate_key", "technology_key", "country_key"]
    missing_fk = fact[fk_columns].isna().sum()
    if missing_fk.sum() > 0:
        raise ValueError(
            f"Se encontraron claves foráneas sin mapear tras el merge:\n{missing_fk[missing_fk > 0]}"
        )

    # --- Solo se incluyen hechos y relaciones justificados por los requisitos ---
    fact["hired_indicator"] = fact["Hired"].astype(int)
    fact = fact.rename(columns={
        "Code Challenge Score": "code_score",
        "Technical Interview Score": "interview_score",
    })

    fact = _add_surrogate_key(fact, "application_key")

    fact_columns = [
        "application_key",
        "date_key", "candidate_key", "technology_key", "country_key",  # FKs
        "code_score", "interview_score", "hired_indicator",             # medidas
    ]
    return fact[fact_columns]


# ---------------------------------------------------------------------------
# 3. Orquestación de la transformación dimensional completa
# ---------------------------------------------------------------------------

def build_star_schema(df):
    """
    Ejecuta el flujo completo de la transformación dimensional:
    Datos preparados -> Dimensiones -> Claves sustitutas -> Tabla de hechos.
    """

    dim_date = build_dim_date(df)
    dim_candidate = build_dim_candidate(df)
    dim_technology = build_dim_technology(df)
    dim_country = build_dim_country(df)

    # Se utiliza full_date internamente para asignar date_key
    # a cada aplicación.
    fact_application = build_fact_application(
        df, dim_date, dim_candidate, dim_technology, dim_country
    )

    # full_date fue utilizada como clave natural de apoyo
    # durante la transformación, pero no hace parte de la
    # dimensión final del Star Schema.
    dim_date = dim_date.drop(columns=["full_date"])

    return {
        "dim_date": dim_date,
        "dim_candidate": dim_candidate,
        "dim_technology": dim_technology,
        "dim_country": dim_country,
        "fact_application": fact_application,
    }