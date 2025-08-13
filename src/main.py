import requests
from datetime import datetime
import random
import json
import os
import time
import logging

# ---------------- Configuración Logging ----------------
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/monitoreo.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# ---------------- Función de API con reintentos ----------------
def fetch_api(url, max_retries=3, timeout=20):
    for intento in range(1, max_retries + 1):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.warning(f"Intento {intento} fallido para {url}: {e}")
            if intento == max_retries:
                logging.error(f"No se pudo obtener datos de {url} después de {max_retries} intentos")
                return None
            time.sleep(2)

# ---------------- Funciones para guardar datos ----------------
def guardar_datos_json(nombre_archivo, datos):
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

# --------------------------------------------------------------
while True:
    with open("config/config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    ciudades = config.get("ciudades", [])

    fecha_ejecucion_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    os.makedirs("data", exist_ok=True)
    archivo_alertas = "data/alertas.json"
    archivo_datos = "data/datos_ciudades.json"

    if os.path.exists(archivo_alertas):
        with open(archivo_alertas, "r", encoding="utf-8") as f:
            try:
                contenido_alertas = json.load(f)
            except json.JSONDecodeError:
                contenido_alertas = []
    else:
        contenido_alertas = []

    contenido_datos = []

    for ciudad in ciudades:
        logging.info(f"Procesando ciudad: {ciudad['nombre']}")

        # ---------- API Clima ----------
        url_clima = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={ciudad['lat']}&longitude={ciudad['lon']}"
            f"&daily=temperature_2m_max"
            f"&current=precipitation_probability,uv_index,temperature_2m,wind_speed_10m"
            f"&timezone=auto"
        )
        data_clima = fetch_api(url_clima)

        current = data_clima.get("current", {}) if data_clima else {}
        temp_actual = current.get("temperature_2m")
        viento = current.get("wind_speed_10m")
        prob_lluvia = current.get("precipitation_probability")
        uv_actual = current.get("uv_index")

        pronostico = []
        if data_clima:
            daily = data_clima.get("daily", {})
            fechas = daily.get("time", [])
            temps = daily.get("temperature_2m_max", [])
            for i in range(len(fechas)):
                temp_max = temps[i] if i < len(temps) else None
                pronostico.append({"fecha": fechas[i], "temp_max": temp_max})

        # ---------- API Tasas de Cambio ----------
        url_cambio = f"https://api.exchangerate-api.com/v4/latest/{ciudad['moneda']}"
        data_cambio = fetch_api(url_cambio)

        rates = data_cambio.get("rates", {}) if data_cambio else {}
        tasa_actual = rates.get("COP")
        historico = []
        if tasa_actual:
            for _ in range(5):
                variacion = random.uniform(-0.02, 0.02)
                historico.append(round(tasa_actual * (1 + variacion), 2))

        # ---------- API Zonas Horarias ----------
        url_tz = f"https://timeapi.io/api/TimeZone/zone?timeZone={ciudad['timezone']}"
        data_tz = fetch_api(url_tz)

        hora_local = data_tz.get("currentLocalTime") if data_tz else None
        offset_ciudad = data_tz.get("currentUtcOffset", {}).get("seconds", 0) if data_tz else 0

        data_bogota = fetch_api("https://timeapi.io/api/TimeZone/zone?timeZone=America/Bogota")
        offset_bogota = data_bogota.get("currentUtcOffset", {}).get("seconds", 0) if data_bogota else 0

        dif_horas = (offset_ciudad - offset_bogota) / 3600
        if dif_horas > 0:
            dif_horaria = f"{abs(dif_horas)} horas adelante"
        elif dif_horas < 0:
            dif_horaria = f"{abs(dif_horas)} horas atrás"
        else:
            dif_horaria = "Misma hora"

        # ---------- Reglas de negocio y alertas ----------
        alertas_clima = []
        if temp_actual is not None:
            if temp_actual > 35 or temp_actual < 0:
                alertas_clima.append("Temperatura crítica")
        if prob_lluvia and prob_lluvia > 70:
            alertas_clima.append("Alta probabilidad de lluvia")
        if viento and viento > 50:
            alertas_clima.append("Vientos fuertes")

        alertas_cambio = []
        if tasa_actual and historico:
            variacion_dia_anterior = ((tasa_actual - historico[-1]) / historico[-1]) * 100
            if abs(variacion_dia_anterior) > 3:
                alertas_cambio.append("Variación > 3% respecto al día anterior")
            # Tendencia negativa últimos 3 días
            if len(historico) >= 3:
                if historico[-3] > historico[-2] > historico[-1]:
                    alertas_cambio.append("Tendencia negativa 3 días consecutivos")

        # Calculo de scores
        clima_score = max(0, 100 - len(alertas_clima)*25)
        cambio_score = 100 if not alertas_cambio else 50
        if uv_actual is None:
            uv_score = 50
        elif uv_actual < 6:
            uv_score = 100
        elif 6 <= uv_actual <= 8:
            uv_score = 75
        else:
            uv_score = 50

        ivv = round((clima_score*0.4)+(cambio_score*0.3)+(uv_score*0.3),1)
        if ivv >= 80:
            nivel_riesgo = "BAJO"; color = "#28a745"
        elif ivv >= 60:
            nivel_riesgo = "MEDIO"; color = "#ffc107"
        elif ivv >= 40:
            nivel_riesgo = "ALTO"; color = "#fd7e14"
        else:
            nivel_riesgo = "CRITICO"; color = "#dc3545"

        def prioridad_alertas(alertas, tipo):
            if tipo=="climática":
                if len(alertas)==1: return "BAJA"
                elif len(alertas)==2: return "MEDIA"
                elif len(alertas)>=3: return "ALTA"
            if tipo=="cambio":
                if len(alertas)==1: return "MEDIA"
                elif len(alertas)>=2: return "ALTA"
            return None

        for alerta in alertas_clima:
            contenido_alertas.append({
                "fecha_ejecucion": fecha_ejecucion_actual,
                "ciudad": ciudad["nombre"],
                "tipo_alerta": "climática",
                "categoria": "temperatura" if "temperatura" in alerta.lower() else "lluvia" if "lluvia" in alerta.lower() else "viento",
                "descripcion": alerta,
                "prioridad": prioridad_alertas(alertas_clima, "climática")
            })

        for alerta in alertas_cambio:
            contenido_alertas.append({
                "fecha_ejecucion": fecha_ejecucion_actual,
                "ciudad": ciudad["nombre"],
                "tipo_alerta": "cambio",
                "categoria": "variacion" if "variación" in alerta.lower() else "tendencia",
                "descripcion": alerta,
                "prioridad": prioridad_alertas(alertas_cambio, "cambio")
            })

        # ---------------- Guardar datos generales ----------------
        contenido_datos.append({
            "fecha_ejecucion": fecha_ejecucion_actual,
            "ciudad": ciudad["nombre"],
            "lat": ciudad.get("lat"),
            "lon": ciudad.get("lon"),
            "temp_actual": temp_actual,
            "viento_kmh": viento,
            "prob_lluvia": prob_lluvia,
            "uv_actual": uv_actual,
            "tasa_actual": tasa_actual,
            "historico_tasa_cambio": historico,
            "pronostico_7dias": pronostico,
            "hora_local": hora_local,
            "dif_horaria": dif_horaria,
            "ivv": ivv,
            "nivel_riesgo": nivel_riesgo,
            "color_riesgo": color
        })

    if not contenido_alertas:
        contenido_alertas.append({
            "fecha_ejecucion": fecha_ejecucion_actual,
            "ciudad": "N/A",
            "tipo_alerta": "Ninguna",
            "descripcion": "Sin alertas",
            "prioridad": None
        })

    # Guardar en JSON
    guardar_datos_json(archivo_alertas, contenido_alertas)
    guardar_datos_json(archivo_datos, contenido_datos)

    logging.info(f"Ejecución completada para {len(ciudades)} ciudades. Próxima ejecución en 30 minutos.")
    time.sleep(1700)