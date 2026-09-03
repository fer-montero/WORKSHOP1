import pandas as pd
from pathlib import Path


def extract_data():
    """
    Extrae los datos desde el archivo fuente original (candidates.csv)
    y los carga en un DataFrame de Pandas.

    Reglas de la etapa de Extracción:
    - Solo lee el archivo de origen, no lo modifica.
    - El archivo original se conserva intacto en data/raw/.
    - No se realiza ninguna transformación de negocio en esta etapa.

    Returns
    -------
    pd.DataFrame
        DataFrame con los datos crudos, tal como vienen en el origen.
    """

    # Carpeta raíz del proyecto (workshop-1/)
    project_root = Path(__file__).resolve().parent.parent

    # Ruta del archivo fuente original (nunca se sobrescribe)
    source_path = project_root / "data" / "raw" / "candidates.csv"

    if not source_path.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo fuente: {source_path}"
        )

    # Lectura del archivo fuente. El separador es ';'
    df = pd.read_csv(source_path, sep=";")

    return df