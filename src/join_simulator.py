import pandas as pd
import streamlit as st

def suggest_relationships(df_a, df_b):
    suggestions = []
    
    for col_a in df_a.columns:
        unique_a = set(df_a[col_a].dropna().unique())
        if not unique_a:
            continue
            
        len_a = len(unique_a)
        
        for col_b in df_b.columns:
            unique_b = set(df_b[col_b].dropna().unique())
            if not unique_b:
                continue
                
            intersection = unique_a.intersection(unique_b)
            match_pct_a = len(intersection) / len_a
            
            if match_pct_a >= 0.20:
                suggestions.append({
                    'col_a': col_a,
                    'col_b': col_b,
                    'match_pct': match_pct_a * 100,
                    'intersect_count': len(intersection)
                })
                
    suggestions.sort(key=lambda x: x['match_pct'], reverse=True)
    return suggestions

def audit_join(df_a, df_b, col_a, col_b):
    st.markdown("### 🔍 Auditoría Crítica del JOIN")
    
    c1, c2 = st.columns(2)
    type_a = df_a[col_a].dtype
    type_b = df_b[col_b].dtype
    
    if type_a != type_b:
        st.warning(f"⚠️ **Discrepancia de tipos:** Tabla A `{col_a}` es `{type_a}`, pero Tabla B `{col_b}` es `{type_b}`.")
        
    nulls_a = df_a[col_a].isnull().sum()
    nulls_b = df_b[col_b].isnull().sum()
    if nulls_a > 0 or nulls_b > 0:
        st.warning(f"⚠️ **Valores Nulos:** Hay {nulls_a} nulos en `{col_a}` y {nulls_b} nulos en `{col_b}`. Se recomienda limpiar antes de unir.")
        
    a_is_unique = df_a[col_a].is_unique
    b_is_unique = df_b[col_b].is_unique
    
    cardinality = ""
    if a_is_unique and b_is_unique:
        cardinality = "1:1 (Uno a Uno)"
        st.success(f"**Cardinalidad:** {cardinality}")
    elif a_is_unique and not b_is_unique:
        cardinality = "1:N (Uno a Muchos)"
        st.info(f"**Cardinalidad:** {cardinality}")
    elif not a_is_unique and b_is_unique:
        cardinality = "N:1 (Muchos a Uno)"
        st.info(f"**Cardinalidad:** {cardinality}")
    else:
        cardinality = "N:M (Muchos a Muchos)"
        st.error(f"🚨 **Cardinalidad:** {cardinality} - Riesgo de producto cartesiano/duplicación.")

    unique_a = set(df_a[col_a].dropna())
    unique_b = set(df_b[col_b].dropna())
    
    orphan_a = unique_a - unique_b
    orphan_pct = (len(orphan_a) / len(unique_a)) * 100 if len(unique_a) > 0 else 0.0
        
    st.metric(f"Valores Huérfanos en Tabla A (`{col_a}`)", f"{orphan_pct:.1f}%", f"{len(orphan_a)} valores sin cruce en B", delta_color="inverse")

def run_join_simulator(df_a, df_b):
    st.markdown("### Buscador de Relaciones Inteligente")
    
    with st.spinner("Buscando relaciones entre tablas..."):
        suggestions = suggest_relationships(df_a, df_b)
        
    if suggestions:
        st.success(f"Se encontraron {len(suggestions)} posibles relaciones (>20% solapamiento).")
        df_sug = pd.DataFrame(suggestions)
        df_sug.columns = ['Columna Tabla A', 'Columna Tabla B', 'Similitud (%)', 'Valores en Común']
        df_sug['Similitud (%)'] = df_sug['Similitud (%)'].round(2)
        st.dataframe(df_sug, use_container_width=True)
    else:
        st.info("No se encontraron relaciones automáticas robustas (>20% de solapamiento).")
        
    st.divider()
    st.markdown("### Configurador de JOIN Manual")
    
    c1, c2 = st.columns(2)
    col_a = c1.selectbox("Clave en Tabla A", df_a.columns.tolist())
    col_b = c2.selectbox("Clave en Tabla B", df_b.columns.tolist())
    
    if st.button("Evaluar e Integrar Data (JOIN)"):
        audit_join(df_a, df_b, col_a, col_b)
        
        st.subheader("Generando DataFrame Unido (Left Join)...")
        try:
            df_joined = pd.merge(df_a, df_b, left_on=col_a, right_on=col_b, how='left', suffixes=('_A', '_B'))
            st.success("¡Unión exitosa!")
            st.dataframe(df_joined.head(), use_container_width=True)
            return df_joined
        except Exception as e:
            st.error(f"Fallo al realizar el JOIN: {e}")
            return None
            
    return None
