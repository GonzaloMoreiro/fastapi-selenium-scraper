import pandas as pd
import logging
import glob
import os
from datetime import datetime

logger = logging.getLogger(__name__)


def renombrar_archivo(directorio, nombre_base):
    archivos = glob.glob(os.path.join(directorio, "*.csv"))
    if not archivos:
        raise FileNotFoundError("No se encontró ningún archivo descargado para renombrar.")

    archivo_reciente = max(archivos, key=os.path.getctime)
    logger.info(f"Archivo detectado: {archivo_reciente}")

    current_date = datetime.now().strftime("%d-%m-%y")
    nuevo_nombre = f"{nombre_base}-{current_date}.csv"

    subcarpeta = os.path.join(directorio, nombre_base)
    os.makedirs(subcarpeta, exist_ok=True)

    ruta_nueva = os.path.join(subcarpeta, nuevo_nombre)
    os.rename(archivo_reciente, ruta_nueva)

    logger.info(f"Archivo renombrado y movido a: {ruta_nueva}")
    return ruta_nueva


def process_data(directorio, nombre_base):
    patron = os.path.join(directorio, f"{nombre_base}/{nombre_base}*.csv")
    archivos = glob.glob(patron)

    if not archivos:
        raise FileNotFoundError("No se encontró ningún archivo con el patrón esperado")

    archivo_a_usar = max(archivos, key=os.path.getctime)
    logger.info(f"archivo procesado: {archivo_a_usar}")

    for skip in range(8, 13):
        try:
            df = pd.read_csv(archivo_a_usar, skiprows=skip)
            columna_mencion = df['Snippet']
            break
        except Exception:
            continue

    texto_concatenado = '-'.join(columna_mencion)

    valores_a_eliminar = ["NaN", "Unknown", "Redacción"]
    df_filtrado = df[~df['Author'].isin(valores_a_eliminar) & df['Author'].notna()]

    autores = df_filtrado['Author'].unique()
    medios = df['Domain'].unique()

    return pd.DataFrame({
        'text': [texto_concatenado],
        'cantidad_autores': [len(autores)],
        'cantidad_menciones': [len(df)],
        'cantidad_medios': [len(medios)],
        'autores': [' - '.join(autores)],
        'medios': [' - '.join(medios)]
    })
