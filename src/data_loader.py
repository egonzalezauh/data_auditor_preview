import pandas as pd
import streamlit as st
import csv
import io

def load_csv(uploaded_file):
    if uploaded_file is None:
        return None
        
    try:
        # Save current position
        pos = uploaded_file.tell()
        
        # Leemos las primeras lineas para deducir el delimitador
        sample = uploaded_file.read(4096)
        # Intentar decodificar
        try:
            text_sample = sample.decode('utf-8')
        except UnicodeDecodeError:
            try:
                text_sample = sample.decode('latin-1')
            except Exception:
                text_sample = sample.decode('iso-8859-1', errors='replace')
        
        # Reset file position
        uploaded_file.seek(pos)
        
        # Deducir delimitador usando csv.Sniffer
        dialect = csv.Sniffer().sniff(text_sample)
        sep = dialect.delimiter
    except Exception as e:
        # Fallback si falla el sniffer (archivos de 1 columna, etc)
        sep = None
    
    encodings = ['utf-8', 'latin-1', 'iso-8859-1']
    df = None
    
    for enc in encodings:
        try:
            # Restaurar posición cada vez que intentamos de nuevo
            uploaded_file.seek(pos) 
            if sep:
                df = pd.read_csv(uploaded_file, sep=sep, encoding=enc)
            else:
                # pandas engine
                df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding=enc)
            
            # Si se leyó correctamente, rompe el bucle
            break
        except pd.errors.ParserError:
            continue
        except UnicodeDecodeError:
            continue
        except Exception as e:
            # Otro tipo de errores no lo intentamos en otro encoding
            st.error(f"Error inesperado al leer el archivo con {enc}: {e}")
            return None
            
    if df is None:
        st.error("No se pudo leer el archivo CSV. Verifica el formato, el delimitador o la codificación.")
        
    return df

def display_health_check(df, filename):
    mem_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
    rows, cols = df.shape
    duplicated_rows = df.duplicated().sum()
    
    st.markdown("### 📊 Visor de Salud del Archivo")
    st.markdown(f"**Archivo:** `{filename}`")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Filas", f"{rows:,}")
    c2.metric("Columnas", f"{cols:,}")
    c3.metric("Tamaño en Memoria", f"{mem_mb:.2f} MB")
    c4.metric("Filas Duplicadas", f"{duplicated_rows:,}")
    
    if mem_mb > 500:
        st.warning("⚠️ Advertencia: El tamaño en memoria supera los 500 MB. Las operaciones complejas podrían ralentizar tu equipo.")
        
    if duplicated_rows > 0:
        st.error(f"⚠️ Se detectaron {duplicated_rows:,} filas 100% idénticas (completamente duplicadas).")
        
    st.write("Vista previa de las primeras 3 filas:")
    st.dataframe(df.head(3), use_container_width=True)
    st.divider()
