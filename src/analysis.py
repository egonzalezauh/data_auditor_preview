import pandas as pd
import streamlit as st
import plotly.express as px
import itertools
from src.data_loader import display_health_check

def perform_individual_analysis(df, filename):
    st.header("Análisis Individual de la Tabla")
    st.markdown("---")
    
    tab_salud, tab_nulos, tab_metricas, tab_categorias, tab_dimensional = st.tabs([
        "🩺 Resumen y Salud", 
        "⚠️ Análisis de Nulos", 
        "🔢 Métricas y Fechas", 
        "📊 Detección/Categorías", 
        "🧩 Modelo Dimensional"
    ])
    
    with tab_salud:
        display_health_check(df, filename)
        
    with tab_nulos:
        st.markdown("### ⚠️ Auditoría de Datos Faltantes (Nulos)")
        null_counts = df.isnull().sum()
        null_pct = (null_counts / len(df)) * 100
        null_df = pd.DataFrame({'Nulos': null_counts, 'Porcentaje (%)': null_pct}).sort_values(by='Porcentaje (%)', ascending=False)
        null_df = null_df[null_df['Nulos'] > 0]
        
        if null_df.empty:
            st.success("✨ ¡Excelente! No se encontraron valores nulos en ninguna columna.")
        else:
            st.warning(f"Se encontraron valores nulos en {len(null_df)} columnas.")
            st.dataframe(null_df.style.format({'Porcentaje (%)': '{:.2f}%'}), use_container_width=True)
            
    with tab_metricas:
        st.markdown("### 🔢 Perfilado de Métricas Continuas")
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            metrics_data = []
            for col in numeric_cols:
                metrics_data.append({
                    "Columna": col,
                    "Mínimo": df[col].min(),
                    "Máximo": df[col].max(),
                    "Promedio": df[col].mean(),
                    "Cant. de Ceros (0)": (df[col] == 0).sum()
                })
            st.dataframe(pd.DataFrame(metrics_data).set_index("Columna"), use_container_width=True)
        else:
            st.info("No se detectaron columnas numéricas para perfilar.")
            
        st.markdown("### 📅 Rango Temporal (Fechas)")
        date_cols = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col]) or 'fecha' in str(col).lower() or 'date' in str(col).lower()]
        has_dates = False
        for col in date_cols:
            try:
                # Usar dayfirst=True evita que 12/03/2026 (12 de Marzo) se lea como 3 de Diciembre en formato gringo
                d_series = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
                min_date = d_series.min()
                max_date = d_series.max()
                if not pd.isnull(min_date):
                    has_dates = True
                    st.info(f"**{col}:** Rango desde `{min_date.date() if hasattr(min_date, 'date') else min_date}` hasta `{max_date.date() if hasattr(max_date, 'date') else max_date}`")
            except:
                pass
        if not has_dates:
            st.info("No se detectaron columnas de fechas o rangos extraíbles.")
            
    with tab_categorias:
        st.markdown("### 🔑 Detección de Claves (Primary Keys)")
        detect_primary_keys(df)
        st.markdown("---")
        st.markdown("### 📊 Perfilado Categórico")
        profile_categorical_columns(df)
        
    with tab_dimensional:
        st.markdown("### 🧩 Clasificación del Modelo Dimensional")
        classify_dimensional_model(df)

def detect_primary_keys(df):
    total_rows = len(df)
    if total_rows == 0:
        st.write("El DataFrame está vacío.")
        return
        
    pk_candidates = []
    
    # 1. 100% no nulos y 100% unicidad en 1 columna
    for col in df.columns:
        if df[col].isnull().sum() == 0 and df[col].nunique() == total_rows:
            pk_candidates.append(col)
            
    if pk_candidates:
        st.success(f"**Candidatas a Primary Key Simple encontradas:** {', '.join(pk_candidates)}")
    else:
        st.warning("No se encontró ninguna clave primaria simple (100% no nula y única). Buscando combinaciones de hasta 6 columnas...")
        
        # Optimize by only considering columns without nulls for the PK
        valid_cols = [c for c in df.columns if df[c].isnull().sum() == 0]
        
        if not valid_cols:
            st.error("No hay columnas sin valores nulos. Es imposible formar una Primary Key confiable.")
            return

        if len(valid_cols) > 20:
            st.warning("Demasiadas columnas sin nulos, limitando búsqueda a las primeras 20 por rendimiento.")
            valid_cols = valid_cols[:20]
            
        found_composite = False
        
        # Iterate from combinations of 2 up to 6
        for r in range(2, 7):
            if found_composite:
                break
                
            for combo in itertools.combinations(valid_cols, r):
                if df[list(combo)].drop_duplicates().shape[0] == total_rows:
                    cols_str = '`, `'.join(combo)
                    st.info(f"**Sugerencia de Clave Compuesta:** (`{cols_str}`)")
                    found_composite = True
                    break # Stop at the first valid combination found
                    
        if not found_composite:
            st.error("Tampoco se encontró una clave primaria compuesta viable entre combinaciones de hasta 6 columnas.")

def profile_categorical_columns(df):
    total_rows = len(df)
    cat_cols = []
    
    for col in df.columns:
        # Avoid treating dates as categorical, checking both dtype and column names
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            continue
        col_lower = str(col).lower()
        if 'fecha' in col_lower or 'date' in col_lower or 'time' in col_lower:
            continue
            
        unique_count = df[col].nunique(dropna=True)
        # Regla: < 50 únicos O porcentaje de únicos < 5% del total
        if unique_count > 0 and (unique_count < 50 or unique_count < 0.05 * total_rows):
            cat_cols.append(col)
            
    if not cat_cols:
        st.write("No se detectaron columnas categóricas que cumplan las reglas (únicos < 50 o < 5% del total).")
        return
        
    st.write(f"Columnas categóricas detectadas ({len(cat_cols)}): {', '.join(cat_cols)}")
    
    selected_cat = st.selectbox("Selecciona una columna categórica para ver su distribución:", cat_cols)
    if selected_cat:
        # Calcular conteo y porcentaje
        counts = df[selected_cat].value_counts().reset_index()
        counts.columns = [selected_cat, 'Conteo']
        counts['Porcentaje'] = (counts['Conteo'] / total_rows * 100).round(2)
        
        unique_count = df[selected_cat].nunique(dropna=True)
        
        if unique_count <= 10:
            # Ordenar ascendente para gráfico horizontal
            counts_chart = counts.sort_values(by='Conteo', ascending=True)
            
            # Plotly chart para 10 o menos categorías
            fig = px.bar(
                counts_chart, 
                y=selected_cat, 
                x='Conteo', 
                orientation='h',
                title=f"Distribución de {selected_cat}",
                text=counts_chart.apply(lambda row: f"{row['Porcentaje']}%", axis=1)
            )
            # Asegurarse de mantener el orden en el grid categórico
            fig.update_layout(yaxis={'categoryorder':'total ascending', 'type':'category'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Mostrar tabla Top 10 para más de 10 categorías
            st.write(f"**Top 10 valores de `{selected_cat}`** (de {unique_count} categorías totales):")
            
            counts_top = counts.head(10).copy()
            # Opcional: formatear string para la tabla
            counts_top['Porcentaje'] = counts_top['Porcentaje'].astype(str) + '%'
            
            # Indice base 1 en la visualización
            counts_top.index = range(1, len(counts_top) + 1)
            
            st.dataframe(counts_top, use_container_width=True)

def classify_dimensional_model(df):
    total_cols = len(df.columns)
    
    text_desc_cols = []
    numeric_continuous_cols = []
    id_key_cols = []
    date_cols = []
    fact_markers = []
    
    id_keywords = ['id', 'key', 'cod', 'num', 'serial', 'nro', 'no']
    metric_keywords = ['total', 'monto', 'precio', 'price', 'cost', 'qty', 'cantidad', 'neto', 'factura', 'venta', 'amount']
    
    for col in df.columns:
        col_lower = str(col).lower()
        dtype = df[col].dtype
        
        is_date = pd.api.types.is_datetime64_any_dtype(dtype) or 'fecha' in col_lower or 'date' in col_lower
        is_fact = any(kw in col_lower for kw in metric_keywords)
        is_id = any(kw in col_lower for kw in id_keywords)
        
        # Asignación Mutuamente Exclusiva (Prioridad)
        if is_date:
            date_cols.append(col)
        elif is_fact:
            fact_markers.append(col)
        elif is_id:
            id_key_cols.append(col)
        elif pd.api.types.is_numeric_dtype(dtype):
            numeric_continuous_cols.append(col)
        else:
            text_desc_cols.append(col)
            
    total_cols = len(df.columns)
    
    # En un esquema mutuamente exclusivo, las columnas de texto puro + los IDs conforman la "naturaleza descriptiva" de la dimensión.
    descriptive_ratio = (len(text_desc_cols) + len(id_key_cols)) / total_cols if total_cols > 0 else 0
    
    classification = "Desconocida"
    detalles = ""
    
    # 1. Chequeo de Negocio: Si hay marcadores de hechos transaccionales evidentes
    if len(fact_markers) >= 1 and (len(date_cols) >= 1 or len(numeric_continuous_cols) >= 1):
        classification = "Tabla de Hechos"
        detalles = f"Identificamos {len(fact_markers)} marcador(es) transaccional(es) fuerte(s) (ej. totales, facturas, cantidades) soportado por métricas o fechas. Propio de un Evento/Transacción."
        
        if len(date_cols) == 1:
            classification += " (Transaccional)"
        elif len(date_cols) >= 3:
            classification += " (Instantánea Acumulativa)"
            
    # 2. Regla Descriptiva: Si no hay transacciones claras, y la mayoría son Textos e IDs.
    elif descriptive_ratio >= 0.50:
        classification = "Tabla de Dimensión"
        detalles = f"Se determinó como Dimensión porque carece de marcadores transaccionales claros y el {(descriptive_ratio*100):.1f}% de sus columnas son de naturaleza descriptiva (Texto puro + IDs)."
    else:
        classification = "Tabla de Hechos"
        detalles = "Múltiples columnas de métricas continuas puras. Sugiere el registro de un evento cuantificable continuo."
        
        if len(date_cols) == 1:
            classification += " (Transaccional)"
            detalles += " Tiene 1 fecha principal, sugiriendo un evento periódico."
        elif len(date_cols) >= 3:
            classification += " (Instantánea Acumulativa)"
            detalles += " Tiene múltiples fechas, rastreo de un flujo de vida."
        else:
            if len(numeric_continuous_cols) >= 1:
                classification += " (Transaccional sin fecha explícita)"
            
    st.info(f"**Sugerencia del Modelo Dimensional:** {classification}")
    st.write(f"**Razón:** {detalles}")
    
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Cols Descriptivas", len(text_desc_cols))
    c2.metric("Métricas Numéricas", len(numeric_continuous_cols))
    c3.metric("IDs/Claves", len(id_key_cols))
    c4.metric("Fechas", len(date_cols))
    c5.metric("Marcadores Transacc.", len(fact_markers))
    
    st.markdown("#### 🧩 Desglose Exclusivo de Columnas")
    
    # Visualización Premium de las agrupaciones (Mutuamente excluyentes)
    with st.container(border=True):
        if date_cols:
            st.markdown(f"**📅 Fechas ({len(date_cols)}):** " + " • ".join([f"`{c}`" for c in date_cols]))
        if fact_markers:
            st.markdown(f"**💰 Marcadores Transaccionales ({len(fact_markers)}):** " + " • ".join([f"`{c}`" for c in fact_markers]))
        if id_key_cols:
            st.markdown(f"**🔑 IDs / Claves ({len(id_key_cols)}):** " + " • ".join([f"`{c}`" for c in id_key_cols]))
        if numeric_continuous_cols:
            st.markdown(f"**🔢 Métricas Numéricas ({len(numeric_continuous_cols)}):** " + " • ".join([f"`{c}`" for c in numeric_continuous_cols]))
        if text_desc_cols:
            st.markdown(f"**📝 Descriptivas (Texto) ({len(text_desc_cols)}):** " + " • ".join([f"`{c}`" for c in text_desc_cols]))
            
    with st.expander("📚 ¿Qué significan estos resultados? (Leer Explicación Formativa)"):
        st.markdown('''
**1. Tabla de Dimensión:**
Es una tabla que almacena el "contexto" o las características informativas del negocio (el 'quién', 'qué' o 'dónde'). Suele tener una columna de llave primaria y muchísimas columnas de texto descriptivo (Ej: Catálogo de *Clientes* o Maestro de *Productos*). 

**2. Tabla de Hechos (Fact Table):**
Es la tabla núcleo que almacena los "eventos", procesos o transacciones medibles de tu negocio. Una verdadera tabla de hechos contiene principalmente llaves foráneas (IDs) que conectan hacia las Tablas de Dimensión, y métricas puras formadas por números que se pueden sumar, contar o promediar (Ej: tabla de *Ventas* o *Inventario*).

Según el manejo del tiempo, un Hecho puede ser:
- **Transaccional:** Registra un evento que sucede en un punto muy específico en el tiempo. Por eso tiene típicamente 1 sola fecha principal en su estructura (Ej: La `fecha_venta` en un tique de supermercado).
- **Instantánea Acumulativa (Accumulating Snapshot):** Registra el ciclo de vida de un flujo completo que tiene múltiples pasos o fases a lo largo del tiempo. Se identifican fácilmente porque su fila concentra múltiples fechas cruzadas (Ej: `creacion_pedido`, `fecha_envio`, `fecha_entrega` y `fecha_facturacion`).
- **Transaccional sin fecha explícita:** Situaciones especiales donde el evento numérico o captura del sistema no requiere o no guardó un Timestamp, pero el modelo conserva múltiples métricas continuas ligadas a llaves.
        ''')
