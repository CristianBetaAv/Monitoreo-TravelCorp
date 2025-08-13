import requests
from datetime import datetime
import random
import json
import os

ciudades = [
    {"nombre": "Nueva York", "lat": 40.7128, "lon": -74.0060, "moneda": "USD", "timezone": "America/New_York"},
    {"nombre": "Londres", "lat": 51.5074, "lon": -0.1278, "moneda": "GBP", "timezone": "Europe/London"},
    {"nombre": "Tokio", "lat": 35.6762, "lon": 139.6503, "moneda": "JPY", "timezone": "Asia/Tokyo"},
    {"nombre": "São Paulo", "lat": -23.5505, "lon": -46.6333, "moneda": "BRL", "timezone": "America/Sao_Paulo"},
    {"nombre": "Sídney", "lat": -33.8688, "lon": 151.2093, "moneda": "AUD", "timezone": "Australia/Sydney"}
]

fecha_ejecucion_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

archivo_alertas = os.path.join("data", "alertas.json")
archivo_datos = os.path.join("data", "datos_ciudades.json")

os.makedirs("data", exist_ok=True)

if os.path.exists(archivo_alertas):
    with open(archivo_alertas, "r", encoding="utf-8") as f:
        contenido_alertas = json.load(f)
else:
    contenido_alertas = []

contenido_datos = []

for ciudad in ciudades:
    print(f"\n==================== {ciudad['nombre']} ====================")
    # ---------- API Clima (Open-Meteo) ----------
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={ciudad['lat']}&longitude={ciudad['lon']}"
        f"&daily=temperature_2m_max"
        f"&current=precipitation_probability,uv_index,temperature_2m,wind_speed_10m"
        f"&timezone=auto"
    )

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        
        current = data["current"] # Datos actuales
        temp_actual = current.get("temperature_2m")
        viento = current.get("wind_speed_10m")
        prob_lluvia = current.get("precipitation_probability")
        uv_actual = current.get("uv_index")

        daily = data["daily"] # Pronóstico diario (7 días)
        pronostico = []
        for i in range(len(daily["time"])):
            pronostico.append({
                "fecha": daily["time"][i],
                "temp_max": daily["temperature_2m_max"][i]
            })

# ---------- API Tasas de Cambio ----------
    url = (f"https://api.exchangerate-api.com/v4/latest/{ciudad['moneda']}")
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        current = data["rates"]
        tasa_actual = current.get("COP")

        # Histórico últimos 5 días con variación ±2%
        historico = []
        for _ in range(5):
            variacion = random.uniform(-0.02, 0.02)  # ±2%
            historico.append(round(tasa_actual * (1 + variacion), 2))

# ---------- API Zonas Horarias ----------
    url = (
        f"https://timeapi.io/api/TimeZone/zone"
        f"?timeZone={ciudad['timezone']}"
        )

    response = requests.get(url)

    if response.status_code == 200:
        data_ciudad = response.json()

        hora_local = data_ciudad["currentLocalTime"]
        offset_ciudad = data_ciudad["currentUtcOffset"]["seconds"]

        # Obtener Bogotá
        url_bogota = "https://timeapi.io/api/TimeZone/zone?timeZone=America/Bogota"
        resp_bogota = requests.get(url_bogota)
        if resp_bogota.status_code == 200:
            offset_bogota = resp_bogota.json()["currentUtcOffset"]["seconds"]

            dif_horas = (offset_ciudad - offset_bogota) / 3600  # Calcular diferencia en horas (seg a hrs)

            if dif_horas > 0:
                dif_horaria = f"{abs(dif_horas)} horas adelante"
            elif dif_horas < 0:
                dif_horaria = f"{abs(dif_horas)} horas atrás"
            else:
                dif_horaria = "Misma hora"

# ---------- Reglas de negocio ----------
    alertas_clima = [] # ---------- Sistema de alertas climáticas ----------

    if temp_actual > 35 or temp_actual < 0:
        alertas_clima.append("Temperatura crítica")
    if prob_lluvia > 70:
        alertas_clima.append("Alta probabilidad de lluvia")
    if viento > 50:
        alertas_clima.append("Vientos fuertes")

    clima_score = 100 - (len(alertas_clima) * 25) # Clima_Score = 100 - (alertas_climaticas * 25)
    if clima_score < 0:
        clima_score = 0

    alertas_cambio = [] # ---------- Sistema de alertas de tipo de cambio ----------

    variacion_dia_anterior = ((tasa_actual - historico[-1]) / historico[-1]) * 100 # ((Valor Final - Valor Inicial) / Valor Inicial) * 100

    if abs(variacion_dia_anterior) > 3:
        alertas_cambio.append("Variación > 3% respecto al día anterior")

    inicio = len(historico) - 3 # Tendencia negativa 3 días consecutivos
    fin = len(historico) - 1
    comparaciones = []

    for i in range(inicio, fin):
        es_descenso = historico[i] > historico[i + 1]
        comparaciones.append(es_descenso)

    tendencia_negativa = all(comparaciones) # Si todas son True, hay tendencia negativa

    if tendencia_negativa:
        alertas_cambio.append("Tendencia negativa 3 días consecutivos")


    if not alertas_cambio: # Cambio_Score = 100 si estable, 50 si volátil 
        cambio_score = 100
    else:
        cambio_score = 50

    if uv_actual < 6: # UV_Score = 100 si UV < 6, 75 si UV 6-8, 50 si UV > 8
        uv_score = 100
    elif 6 <= uv_actual <= 8:
        uv_score = 75
    else:
        uv_score = 50

    ivv = round((clima_score * 0.4) + (cambio_score * 0.3) + (uv_score * 0.3), 1) # IVV

    if ivv >= 80: # Color y nivel de riesgo
        nivel_riesgo = "BAJO"
        color = "#28a745"
    elif ivv >= 60:
        nivel_riesgo = "MEDIO"
        color = "#ffc107"
    elif ivv >= 40:
        nivel_riesgo = "ALTO"
        color = "#fd7e14"
    else:
        nivel_riesgo = "CRITICO"
        color = "#dc3545"

# ---------------- Guardar alertas ----------------
    if len(alertas_clima) == 1: # Alertas climáticas
        prioridad_clima = "BAJA"
    elif len(alertas_clima) == 2:
        prioridad_clima = "MEDIA"
    elif len(alertas_clima) >= 3:
        prioridad_clima = "ALTA"
    else:
        prioridad_clima = None

    for alerta in alertas_clima: # Guardar alertas climáticas
        contenido_alertas.append({
            "fecha_ejecucion": fecha_ejecucion_actual,
            "ciudad": ciudad["nombre"],
            "tipo_alerta": "climática",
            "categoria": "temperatura" if "temperatura" in alerta.lower() else "lluvia" if "lluvia" in alerta.lower() else "viento",
            "descripcion": alerta,
            "prioridad": prioridad_clima
        })

    if len(alertas_cambio) == 1: # Alertas de tasa de cambio
        prioridad_cambio = "MEDIA"
    elif len(alertas_cambio) >= 2:
        prioridad_cambio = "ALTA"
    else:
        prioridad_cambio = None

    for alerta in alertas_cambio: # Guardar alertas tasa de cambio
        contenido_alertas.append({
            "fecha_ejecucion": fecha_ejecucion_actual,
            "ciudad": ciudad["nombre"],
            "tipo_alerta": "cambio",
            "categoria": "variacion" if "variación" in alerta.lower() else "tendencia",
            "descripcion": alerta,
            "prioridad": prioridad_cambio
        })

# ---------------- Guardar datos generales ----------------
    contenido_datos.append({
        "fecha_ejecucion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ciudad": ciudad["nombre"],
        "lat": ciudad["lat"],
        "lon": ciudad["lon"],
        "temp_actual": temp_actual,
        "viento_kmh": viento,
        "prob_lluvia": prob_lluvia,
        "uv_actual": uv_actual,
        "tasa_actual": tasa_actual,
        "historico_tasa_cambio": historico,
        "pronostico_7dias": pronostico,
        "ivv": ivv,
        "nivel_riesgo": nivel_riesgo,
        "color_riesgo": color
    })

# ---------------- Guardar en JSON ----------------
with open(archivo_alertas, "w", encoding="utf-8") as f:
    json.dump(contenido_alertas, f, ensure_ascii=False, indent=2)

with open(archivo_datos, "w", encoding="utf-8") as f:
    json.dump(contenido_datos, f, ensure_ascii=False, indent=2)

print(f"\n✅ Datos y alertas guardados para {len(ciudades)} ciudades")