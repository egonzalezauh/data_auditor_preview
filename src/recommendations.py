import pandas as pd
import streamlit as st
import plotly.express as px

def run_recommendations_engine(df):
    st.markdown("### 🤖 Motor de Recomendaciones y Agrupación")
    
    total_rows = len(df)
    
    dimensions = []
    for col in df.columns:
        nunique = df[col].nunique(dropna=True)
        if nunique < 0.05 * total_rows and nunique > 0 and nunique < 100:
            dimensions.append(col)
            
    dimensions = dimensions[:5]
    
    metrics = []
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            col_lower = str(col).lower()
            if 'id' not in col_lower and 'key' not in col_lower and 'year' not in col_lower and 'año' not in col_lower:
                metrics.append(col)
                
    date_cols = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]
    for col in df.columns:
        if ('fecha' in str(col).lower() or 'date' in str(col).lower()) and col not in date_cols:
            try:
                if not df[col].dropna().empty:
                     pd.to_datetime(df[col].dropna().iloc[0])
                     date_cols.append(col)
            except:
                pass

    if not metrics:
        st.info("No se encontraron suficientes columnas numéricas medibles para realizar sugerencias analíticas.")
        return
        
    sugerencias = []
    
    if dimensions and metrics:
        for dim in dimensions[:2]:
            for met in metrics[:2]:
                sugerencias.append({
                    "label": f"Ver Suma de [{met}] agrupado por [{dim}]",
                    "type": "sum",
                    "dim": dim,
                    "met": met
                })
                sugerencias.append({
                    "label": f"Ver Promedio de [{met}] agrupado por [{dim}]",
                    "type": "mean",
                    "dim": dim,
                    "met": met
                })
                
    if date_cols and metrics:
        dcol = date_cols[0]
        for met in metrics[:2]:
            sugerencias.append({
                "label": f"Ver Evolución Mensual (Suma) de [{met}] por [{dcol}]",
                "type": "time_sum",
                "dim": dcol,
                "met": met
            })
            
    if not sugerencias:
        st.info("No se hallaron combinaciones claras. Intenta con un dataset más variado.")
        return
        
    options = {s["label"]: s for s in sugerencias}
    
    st.write("Selecciona una sugerencia analítica para previsualizar:")
    selected_label = st.selectbox("Sugerencias:", list(options.keys()))
    
    if st.button("Ejecutar Análisis"):
        conf = options[selected_label]
        dim = conf["dim"]
        met = conf["met"]
        agg_type = conf["type"]
        
        try:
            if agg_type in ["sum", "mean"]:
                if agg_type == "sum":
                    grouped = df.groupby(dim, dropna=False)[met].sum().reset_index()
                    tit = f"Suma Total de {met} por {dim}"
                else:
                    grouped = df.groupby(dim, dropna=False)[met].mean().reset_index()
                    tit = f"Promedio de {met} por {dim}"
                    
                grouped = grouped.sort_values(by=met, ascending=False)
                
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.dataframe(grouped, use_container_width=True)
                with c2:
                    fig = px.bar(grouped, x=dim, y=met, title=tit)
                    st.plotly_chart(fig, use_container_width=True)
                    
            elif agg_type == "time_sum":
                temp_df = df[[dim, met]].copy()
                temp_df[dim] = pd.to_datetime(temp_df[dim], errors='coerce')
                temp_df = temp_df.dropna(subset=[dim])
                
                if temp_df.empty:
                    st.warning("La columna de fecha no contiene fechas válidas parseables.")
                else:
                    temp_df['Mes_Agrupado'] = temp_df[dim].dt.to_period('M').astype(str)
                    grouped = temp_df.groupby('Mes_Agrupado')[met].sum().reset_index()
                    grouped = grouped.sort_values(by='Mes_Agrupado')
                    
                    tit = f"Evolución Mensual (Suma) de {met}"
                    
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        st.dataframe(grouped, use_container_width=True)
                    with c2:
                        fig = px.line(grouped, x='Mes_Agrupado', y=met, title=tit, markers=True)
                        st.plotly_chart(fig, use_container_width=True)
                        
        except Exception as e:
            st.error(f"Fallo al calcular la agrupación: {e}")
