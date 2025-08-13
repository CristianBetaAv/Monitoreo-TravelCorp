<<<<<<< HEAD
# Monitoreo de Clima, Tasas de Cambio y Zonas Horarias

## 📌 Arquitectura de la Solución
La solución se compone de un script en Python que:
1. **Obtiene datos en tiempo real** desde APIs públicas:
   - **Open-Meteo** → Clima actual y pronóstico de 7 días.
   - **ExchangeRate-API** → Tasas de cambio y generación de histórico simulado.
   - **TimeAPI** → Hora local y diferencia horaria con Bogotá.
2. **Aplica reglas de negocio** para generar alertas:
   - Alertas climáticas (temperatura extrema, alta probabilidad de lluvia, vientos fuertes).
   - Alertas de tipo de cambio (variaciones bruscas, tendencia negativa).
   - Cálculo del **Índice de Viabilidad de Viaje (IVV)** y asignación de nivel de riesgo.
3. **Guarda la información** en dos archivos JSON:
   - `datos_ciudades.json` → Datos generales de cada ciudad.
   - `alertas.json` → Alertas generadas con prioridad.
4. **Integra con Power BI** para visualización interactiva.

**Estructura de carpetas:**
```bash
config/
  config.json                 # Configuración general
dashboard/
  monitoreo-travelcorp.pbix   # Dashboard en Power BI
data/
  datos_ciudades.json
  alertas.json
src/
  main.py                     # Script principal
.gitignore
README.md
```

## 🗂 Diagrama de Flujo del Proceso
*(Aquí irá el diagrama de flujo en el futuro)*

## ⚙️ Instrucciones de Instalación y Ejecución

### 1️⃣ Requisitos previos
- **Python 3.10** o superior
- Librerías necesarias:
```bash
pip install -r requirements.txt
```

### 2️⃣ Clonar el repositorio
```bash
git clone https://github.com/usuario/monitoreo-clima-cambio-horario.git
cd monitoreo-clima-cambio-horario
```

### 3️⃣ Ejecutar el script
```bash
python src/main.py
```

El sistema creará o actualizará:
  - `data/datos_ciudades.json` → Datos para visualización en Power BI.
  - `data/alertas.json` → Lista de alertas generadas.

# 📂 Descripción de Módulos y Funciones

## `src/main.py`
- **Definición de ciudades**: nombre, coordenadas, moneda y zona horaria.

### Módulo Clima (Open-Meteo)
- Recupera:
  - Temperatura actual
  - Viento
  - Probabilidad de lluvia
  - Índice UV
  - Pronóstico a 7 días

### Módulo Tasas de Cambio (ExchangeRate-API)
- Obtiene tasa actual de moneda local a COP.
- Simula histórico de últimos 5 días (variación ±2%).

### Módulo Zonas Horarias (TimeAPI)
- Obtiene hora local.
- Calcula diferencia horaria con Bogotá.

## Reglas de Negocio

### Alertas Climáticas
- Temperatura extrema (>35°C o <0°C)
- Probabilidad de lluvia >70%
- Viento >50 km/h

### Alertas de Tipo de Cambio
- Variación >3% respecto al día anterior
- Tendencia negativa 3 días consecutivos

### Cálculo IVV
- Fórmula: `(Clima_Score * 0.4) + (Cambio_Score * 0.3) + (UV_Score * 0.3)`
- Asigna color y nivel de riesgo: **BAJO**, **MEDIO**, **ALTO**, **CRÍTICO**

### Priorización de Alertas
- **Clima**:
  - 1 alerta → BAJA
  - 2 alertas → MEDIA
  - ≥3 alertas → ALTA
- **Cambio**:
  - 1 alerta → MEDIA
  - ≥2 alertas → ALTA

## Salida de Datos
- `datos_ciudades.json`: datos generales, pronósticos y nivel de riesgo.
- `alertas.json`: lista de alertas con tipo, categoría, descripción y prioridad.

# 🚨 Manejo de Errores Implementado
- Validación de respuestas de API (`status_code == 200`)
- Uso de `.get()` en diccionarios para evitar `KeyError`
- Creación automática de carpetas (`os.makedirs("data", exist_ok=True)`)
- Verificación de existencia de archivos antes de leerlos
- Control de índices en iteraciones
- Límite inferior para que el `clima_score` no sea negativo

# 📊 Estructura de los Archivos JSON
`datos_ciudades.json`
```bash
[
  {
    "fecha_ejecucion": "2025-08-12 16:46:36",
    "ciudad": "Nueva York",
    "lat": 40.7128,
    "lon": -74.006,
    "temp_actual": 28.2,
    "viento_kmh": 18.8,
    "prob_lluvia": 0,
    "uv_actual": 2.8,
    "tasa_actual": 4060.38,
    "historico_tasa_cambio": [4054.24, 4056.6, 4066.37, 4069.24, 4034.19],
    "pronostico_7dias": [
      {"fecha": "2025-08-12", "temp_max": 31.8},
      {"fecha": "2025-08-13", "temp_max": 33.5}
    ],
    "ivv": 100.0,
    "nivel_riesgo": "BAJO",
    "color_riesgo": "#28a745"
  }
]
```
`alertas.json`
```
[
  {
    "fecha_ejecucion": "2025-08-12 16:46:36",
    "ciudad": "Tokio",
    "tipo_alerta": "climática",
    "categoria": "lluvia",
    "descripcion": "Alta probabilidad de lluvia",
    "prioridad": "MEDIA"
  }
]
```

# 📈 Integración con Power BI

El proyecto incluye un dashboard (`dashboard/monitoreo-travelcorp.pbix`) que consume los archivos JSON para mostrar:

## Vista General
- Mapa con burbujas de color según el **IVV** y nivel de riesgo.
- Tabla con:
  - Ciudad
  - Temperatura actual
  - Índice UV
  - Probabilidad de lluvia
  - Tasa de cambio
  - IVV

## Análisis Temporal
- **Gráfico de líneas**: evolución de temperatura máxima (7 días).
- **Gráfico de barras**: comparación de tasas de cambio.

## Panel de Alertas
- Tabla/lista con alertas activas, prioridad y descripción.
- Histórico filtrado por las últimas 24 horas.

=======
# Monitoreo de Clima, Tasas de Cambio y Zonas Horarias

## 📌 Arquitectura de la Solución
La solución se compone de un script en Python que:
1. **Obtiene datos en tiempo real** desde APIs públicas:
   - **Open-Meteo** → Clima actual y pronóstico de 7 días.
   - **ExchangeRate-API** → Tasas de cambio y generación de histórico simulado.
   - **TimeAPI** → Hora local y diferencia horaria con Bogotá.
2. **Aplica reglas de negocio** para generar alertas:
   - Alertas climáticas (temperatura extrema, alta probabilidad de lluvia, vientos fuertes).
   - Alertas de tipo de cambio (variaciones bruscas, tendencia negativa).
   - Cálculo del **Índice de Viabilidad de Viaje (IVV)** y asignación de nivel de riesgo.
3. **Guarda la información** en dos archivos JSON:
   - `datos_ciudades.json` → Datos generales de cada ciudad.
   - `alertas.json` → Alertas generadas con prioridad.
4. **Integra con Power BI** para visualización interactiva.

**Estructura de carpetas:**
```bash
config/
  config.json                 # Configuración general
dashboard/
  monitoreo-travelcorp.pbix   # Dashboard en Power BI
data/
  datos_ciudades.json
  alertas.json
src/
  main.py                     # Script principal
.gitignore
README.md
```

## 🗂 Diagrama de Flujo del Proceso
*(Aquí irá el diagrama de flujo en el futuro)*

## ⚙️ Instrucciones de Instalación y Ejecución

### 1️⃣ Requisitos previos
- Python 3.10+
- Power BI Desktop o Power BI Service para visualizar los dashboards generados.  
- Conexión a Internet para consultar las APIs.
- Librerías necesarias:
```bash
pip install -r requirements.txt
```

### 2️⃣ Clonar el repositorio
```bash
git clone https://github.com/usuario/monitoreo-clima-cambio-horario.git
cd monitoreo-clima-cambio-horario
```

### 3️⃣ Ejecutar el script
```bash
python src/main.py
```

El sistema creará o actualizará:
  - `data/datos_ciudades.json` → Datos para visualización en Power BI.
  - `data/alertas.json` → Lista de alertas generadas.

# 📂 Descripción de Módulos y Funciones

## `src/main.py`
- **Definición de ciudades**: nombre, coordenadas, moneda y zona horaria.

### Módulo Clima (Open-Meteo)
- Recupera:
  - Temperatura actual
  - Viento
  - Probabilidad de lluvia
  - Índice UV
  - Pronóstico a 7 días

### Módulo Tasas de Cambio (ExchangeRate-API)
- Obtiene tasa actual de moneda local a COP.
- Simula histórico de últimos 5 días (variación ±2%).

### Módulo Zonas Horarias (TimeAPI)
- Obtiene hora local.
- Calcula diferencia horaria con Bogotá.

## Reglas de Negocio

### Alertas Climáticas
- Temperatura extrema (>35°C o <0°C)
- Probabilidad de lluvia >70%
- Viento >50 km/h

### Alertas de Tipo de Cambio
- Variación >3% respecto al día anterior
- Tendencia negativa 3 días consecutivos

### Cálculo IVV
- Fórmula: `(Clima_Score * 0.4) + (Cambio_Score * 0.3) + (UV_Score * 0.3)`
- Asigna color y nivel de riesgo: **BAJO**, **MEDIO**, **ALTO**, **CRÍTICO**

### Priorización de Alertas
- **Clima**:
  - 1 alerta → BAJA
  - 2 alertas → MEDIA
  - ≥3 alertas → ALTA
- **Cambio**:
  - 1 alerta → MEDIA
  - ≥2 alertas → ALTA

## Salida de Datos
- `datos_ciudades.json`: datos generales, pronósticos y nivel de riesgo.
- `alertas.json`: lista de alertas con tipo, categoría, descripción y prioridad.

# 🚨 Manejo de Errores Implementado
- Validación de respuestas de API (`status_code == 200`)
- Uso de `.get()` en diccionarios para evitar `KeyError`
- Creación automática de carpetas (`os.makedirs("data", exist_ok=True)`)
- Verificación de existencia de archivos antes de leerlos
- Control de índices en iteraciones
- Límite inferior para que el `clima_score` no sea negativo

# 📊 Estructura de los Archivos JSON
`datos_ciudades.json`
```bash
[
  {
    "fecha_ejecucion": "2025-08-12 16:46:36",
    "ciudad": "Nueva York",
    "lat": 40.7128,
    "lon": -74.006,
    "temp_actual": 28.2,
    "viento_kmh": 18.8,
    "prob_lluvia": 0,
    "uv_actual": 2.8,
    "tasa_actual": 4060.38,
    "historico_tasa_cambio": [4054.24, 4056.6, 4066.37, 4069.24, 4034.19],
    "pronostico_7dias": [
      {"fecha": "2025-08-12", "temp_max": 31.8},
      {"fecha": "2025-08-13", "temp_max": 33.5}
    ],
    "ivv": 100.0,
    "nivel_riesgo": "BAJO",
    "color_riesgo": "#28a745"
  }
]
```
`alertas.json`
```
[
  {
    "fecha_ejecucion": "2025-08-12 16:46:36",
    "ciudad": "Tokio",
    "tipo_alerta": "climática",
    "categoria": "lluvia",
    "descripcion": "Alta probabilidad de lluvia",
    "prioridad": "MEDIA"
  }
]
```

# 📈 Integración con Power BI

El proyecto incluye un dashboard (`dashboard/monitoreo-travelcorp.pbix`) que consume los archivos JSON para mostrar:

## Vista General
- Mapa con burbujas de color según el **IVV** y nivel de riesgo.
- Tabla con:
  - Ciudad
  - Temperatura actual
  - Índice UV
  - Probabilidad de lluvia
  - Tasa de cambio
  - IVV

## Análisis Temporal
- **Gráfico de líneas**: evolución de temperatura máxima (7 días).
- **Gráfico de barras**: comparación de tasas de cambio.

## Panel de Alertas
- Tabla/lista con alertas activas, prioridad y descripción.
- Histórico filtrado por las últimas 24 horas.
>>>>>>> c4b305a (Nuevas funcionalidades y archivos)
