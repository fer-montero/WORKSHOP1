import pandas as pd


def prepare_data(df):
    """
    Prepara los datos extraídos para el proceso analítico.
    (10.2 Data Preparation — sin cambios respecto a lo ya construido)
    """

    df = df.copy()

    df["Application Date"] = pd.to_datetime(df["Application Date"], format="%Y-%m-%d")

    text_columns = ["First Name", "Last Name", "Email", "Country", "Seniority", "Technology"]
    for col in text_columns:
        df[col] = df[col].str.strip()

    seniority_order = ["Intern", "Trainee", "Junior", "Mid-Level", "Senior", "Lead", "Architect"]
    df["Seniority"] = pd.Categorical(df["Seniority"], categories=seniority_order, ordered=True)
    df["Technology"] = df["Technology"].astype("category")
    df["Country"] = df["Country"].astype("category")

    missing_after = df.isna().sum()
    if missing_after.sum() > 0:
        print("ADVERTENCIA: se encontraron valores nulos tras la preparación:")
        print(missing_after[missing_after > 0])

    return df


def apply_business_rules(df):
    """
    Aplica la regla de negocio de contratación (10.3 Business Transformation).

    Regla de negocio:
        HIRED = (Code Challenge Score >= 7) AND (Technical Interview Score >= 7)

    Importante: esta función SOLO añade un atributo derivado ('Hired').
    No elimina ni filtra ningún registro. El grano del modelo dimensional
    es "una fila = una aplicación", por lo que las aplicaciones NOT HIRED
    deben conservarse: R1 (tendencias de contratación) y R2 (análisis por
    tecnología) necesitan comparar volúmenes y proporciones de HIRED vs
    NOT HIRED, algo imposible si se eliminaran los no contratados.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame ya preparado (salida de prepare_data()).

    Returns
    -------
    pd.DataFrame
        Mismo DataFrame con la columna adicional 'Hired' (booleano).
    """

    df = df.copy()  # nunca modificar el DataFrame recibido

    df["Hired"] = (
        (df["Code Challenge Score"] >= 7)
        & (df["Technical Interview Score"] >= 7)
    )

    return df