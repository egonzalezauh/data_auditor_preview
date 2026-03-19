# 📊 Data Auditor Pro

Bienvenido a **Data Auditor Pro**, una potente herramienta interactiva construida con Streamlit que te ayuda a perfilar, auditar y cruzar conjuntos de información a partir de archivos CSV de manera local, segura y dinámica.

## 🚀 Características Principales

1. **🩺 Resumen y Salud del Dato**: Visualiza al instante estadísticas de consumo en memoria, filas, columnas, filas 100% duplicadas y advertencias de rendimiento del archivo.
2. **⚠️ Auditoría de Nulos**: Identifica rápidamente el nivel de completitud de tus tablas y el porcentaje de filas faltantes por cada columna.
3. **🔢 Perfilado de Métricas y Fechas**: Identifica variables continuas presentando automáticamente su Mínimo, Máximo, Promedio y conteo de ceros. También detecta formatos de fechas extrañas y presenta su rango histórico.
4. **🔑 Detección de Primary Keys y Categóricas**: Busca la mejor candidata para ser "Primary Key", buscando claves simples o haciendo combinaciones compuestas de hasta 6 columnas. También examina la distribución porcentual del top 10 en datos categóricos.
5. **🧩 Clasificador del Modelo Dimensional**: Un módulo de IA estadística que deduce heurísticamente si tu tabla subida funge como una **Tabla de Dimensión**, un **Hecho Transaccional** o un **Hecho de Instantánea Acumulativa**.

### 🛠️ Módulos Avanzados (En el código `src/`)
* **🔗 Simulador de Relaciones (JOIN Auditing)**: Enlaza 2 tablas simultáneas y te sugiere la cardinalidad exacta (1:1, 1:N, N:M), el porcentaje de registros huérfanos y alerta disonancias en tipos de datos.
* **🤖 Motor de Recomendaciones**: Basado en las métricas puras y descriptivas detectadas del CSV, autocalcula sugerencias analíticas (como "Ver evolución temporal" o "Dime la suma de X segmentada en Y") dibujando Gráficos de Plotly automáticos a un sólo clic.

## 🔒 Seguridad (Privacy by Design)
Todo el análisis y manipulación de datos ocurre de forma **local y en la memoria RAM** usando Pandas Dataframes en la sesión de Streamlit. No se almacenan historiales, contraseñas, bases de datos ni se envía tu información confidencial hacia la nube. Tus datos mueren al apagar la app.

## ⚙️ Cómo correr este proyecto en tu computadora

**Prerequisitos:** Tener instalado Python 3.9 o superior en tu equipo local.

1. **Clona el repositorio desde GitHub:**
   ```bash
   git clone https://github.com/TU_USUARIO/data_auditor_pro.git
   cd data_auditor_pro
   ```

2. **Crea y activa el entorno virtual (Ejemplo en Windows):**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Instala las paqueterías necesarias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **¡Arranca el Análisis Local!**
   ```bash
   streamlit run app.py
   ```
   *Se abrirá la aplicación automáticamente en tu navegador usando el puerto `http://localhost:8501/`*

---
_Creado y refactorizado para el portafolio de Análisis y Calidad de Datos._
