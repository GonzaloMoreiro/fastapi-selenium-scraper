import os
import time
import logging
import pandas as pd
from datetime import datetime, timedelta

from scraper_redmine import excel_download

logger = logging.getLogger(__name__)


def bolsavoxia_diario(file_path):
    """
    Procesa un archivo Excel para analizar la bolsa de horas y el consumo diario.
    """
    MAX_RETRIES = 3
    WAIT_TIME = 5

    retries = 0
    while retries < MAX_RETRIES:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 1000:
            logger.info("Archivo válido, procesando...")
            break

        logger.warning(
            f"Intento {retries + 1}/{MAX_RETRIES}: "
            "Archivo vacío o corrupto. Reintentando descarga..."
        )
        excel_download()
        retries += 1
        time.sleep(WAIT_TIME)

    if not os.path.exists(file_path) or os.path.getsize(file_path) <= 1000:
        raise ValueError(
            "No se pudo obtener un archivo válido después de varios intentos."
        )

    df = pd.read_excel(file_path, engine="openpyxl", skiprows=4)

    required_columns = [
        'Fecha y hora cierre',
        'Asunto',
        'Tiempo dedicado en horas'
    ]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"La columna '{col}' no se encuentra en el archivo.")

    today = datetime.now()
    yesterday = today - timedelta(days=1)
    yesterday_date = yesterday.date()

    df['Fecha y hora cierre'] = pd.to_datetime(
        df['Fecha y hora cierre'], errors='coerce'
    )

    df_bolsa = df[
        (df['Asunto'].str.contains('Bolsa de horas añadida', na=False)) &
        (df['Fecha y hora cierre'].dt.date <= yesterday_date)
    ]

    if df_bolsa.empty:
        raise ValueError(
            "No se encontró ninguna bolsa de horas añadida válida."
        )

    most_recent_bolsa = df_bolsa.loc[
        df_bolsa['Fecha y hora cierre'].idxmax()
    ]
    bolsa_date = most_recent_bolsa['Fecha y hora cierre']
    hours_in_bolsa = most_recent_bolsa['Tiempo dedicado en horas']

    consumos_dentro_bolsa = df[
        (~df['Asunto'].str.contains('Bolsa de horas añadida', na=False)) &
        (df['Fecha y hora cierre'] >= bolsa_date) &
        (df['Fecha y hora cierre'].dt.date <= yesterday_date)
    ].copy()

    consumos_dentro_bolsa['Tiempo dedicado en horas'] = pd.to_numeric(
        consumos_dentro_bolsa['Tiempo dedicado en horas'],
        errors='coerce'
    )

    consumos_previos = consumos_dentro_bolsa[
        consumos_dentro_bolsa['Fecha y hora cierre'].dt.date < yesterday_date
    ]
    total_consumos_previos = abs(
        consumos_previos['Tiempo dedicado en horas'].sum()
    )

    consumos_dia = consumos_dentro_bolsa[
        consumos_dentro_bolsa['Fecha y hora cierre'].dt.date == yesterday_date
    ]
    total_hours_consumed_today = abs(
        consumos_dia['Tiempo dedicado en horas'].sum()
    )

    remaining_hours = (
        hours_in_bolsa
        - total_consumos_previos
        - total_hours_consumed_today
    )

    project_details = []
    for _, row in consumos_dia.iterrows():
        asunto = row['Asunto'].replace('MMI: ', '').strip()
        if len(asunto) > 100:
            asunto = asunto[:97] + '...'

        hours = abs(row['Tiempo dedicado en horas'])
        project_details.append(
            f" - {asunto} ({hours:.2f} horas)"
        )

    email_body = f"""
Resumen de actividad del {yesterday.strftime('%d/%m/%Y')}:

Detalles de la bolsa:
- Fecha de última bolsa añadida: {bolsa_date.strftime('%d/%m/%Y')}
- Horas iniciales en la bolsa: {hours_in_bolsa:.2f}
- Total de horas consumidas desde renovación de bolsa: {total_consumos_previos:.2f}
- Total de horas consumidas ayer: {total_hours_consumed_today:.2f}
- Total de horas restantes en la bolsa: {remaining_hours:.2f}

Proyectos trabajados ayer:
{chr(10).join(project_details) if project_details else "No se trabajó en ningún proyecto."}
"""
    return email_body


def bolsavoxia_semanal(file_path):
    """
    Genera un resumen semanal de actividad basado en un archivo Excel.
    """
    MAX_RETRIES = 3
    WAIT_TIME = 5

    retries = 0
    while retries < MAX_RETRIES:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 1000:
            logger.info("Archivo válido, procesando...")
            break

        logger.warning(
            f"Intento {retries + 1}/{MAX_RETRIES}: "
            "Archivo vacío o corrupto. Reintentando descarga..."
        )
        excel_download()
        retries += 1
        time.sleep(WAIT_TIME)

    if not os.path.exists(file_path) or os.path.getsize(file_path) <= 1000:
        raise ValueError(
            "No se pudo obtener un archivo válido después de varios intentos."
        )

    df = pd.read_excel(file_path, engine="openpyxl", skiprows=4)

    required_columns = [
        'Fecha y hora cierre',
        'Asunto',
        'Tiempo dedicado en horas'
    ]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"La columna '{col}' no se encuentra en el archivo.")

    today = datetime.now()
    friday = today
    while friday.weekday() != 4:
        friday -= timedelta(days=1)
    monday = friday - timedelta(days=4)

    df['Fecha y hora cierre'] = pd.to_datetime(
        df['Fecha y hora cierre'], errors='coerce'
    )

    df_bolsas = df[
        (df['Asunto'].str.contains('Bolsa de horas añadida', na=False)) &
        (df['Fecha y hora cierre'].dt.date <= friday.date())
    ].sort_values('Fecha y hora cierre')

    if df_bolsas.empty:
        raise ValueError(
            "No se encontró ninguna bolsa de horas añadida válida."
        )

    bolsa_inicial = df_bolsas[
        df_bolsas['Fecha y hora cierre'].dt.date <= monday.date()
    ].iloc[-1]

    bolsa_date_inicial = bolsa_inicial['Fecha y hora cierre']

    consumos_previos = df[
        (~df['Asunto'].str.contains('Bolsa de horas añadida', na=False)) &
        (df['Fecha y hora cierre'] >= bolsa_date_inicial) &
        (df['Fecha y hora cierre'].dt.date < monday.date())
    ].copy()

    total_horas_previas = abs(
        consumos_previos['Tiempo dedicado en horas'].sum()
    ) if not consumos_previos.empty else 0

    bolsas_semana = df_bolsas[
        (df_bolsas['Fecha y hora cierre'].dt.date > monday.date()) &
        (df_bolsas['Fecha y hora cierre'].dt.date <= friday.date())
    ]

    consumos_semana = df[
        (~df['Asunto'].str.contains('Bolsa de horas añadida', na=False)) &
        (df['Fecha y hora cierre'].dt.date >= monday.date()) &
        (df['Fecha y hora cierre'].dt.date <= friday.date())
    ].copy()

    total_horas_semana = abs(
        consumos_semana['Tiempo dedicado en horas'].sum()
    ) if not consumos_semana.empty else 0

    project_details = []
    for _, row in consumos_semana.iterrows():
        asunto = row['Asunto'].replace('MMI: ', '').strip()
        if len(asunto) > 100:
            asunto = asunto[:97] + '...'

        hours = abs(row['Tiempo dedicado en horas'])
        fecha = row['Fecha y hora cierre'].strftime('%d/%m/%Y')
        project_details.append(
            f" - [{fecha}] {asunto} ({hours:.2f} horas)"
        )

    ultima_bolsa = df_bolsas.iloc[-1]
    horas_restantes = (
        ultima_bolsa['Tiempo dedicado en horas']
        - total_horas_previas
        - total_horas_semana
    )

    email_body = f"""
Resumen semanal de actividad ({monday.strftime('%d/%m/%Y')} - {friday.strftime('%d/%m/%Y')}):
Detalles de la bolsa:
- Fecha de última bolsa añadida: {ultima_bolsa['Fecha y hora cierre'].strftime('%d/%m/%Y')}
- Horas iniciales en la bolsa: {ultima_bolsa['Tiempo dedicado en horas']:.2f}
- Horas consumidas antes de esta semana: {total_horas_previas:.2f}
- Horas consumidas esta semana: {total_horas_semana:.2f}
- Horas restantes en la bolsa actual: {horas_restantes:.2f}

{"Bolsas añadidas durante la semana:" if not bolsas_semana.empty else ""}
{chr(10).join([
    f" - {row['Fecha y hora cierre'].strftime('%d/%m/%Y')}: "
    f"{row['Tiempo dedicado en horas']:.2f} horas"
    for _, row in bolsas_semana.iterrows()
]) if not bolsas_semana.empty else ""}

Proyectos trabajados esta semana:
{chr(10).join(project_details) if project_details else "No se trabajó en ningún proyecto esta semana."}
"""
    return email_body
