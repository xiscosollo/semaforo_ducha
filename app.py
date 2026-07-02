import streamlit as st
import time
import os
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(page_title="Semáforo Ducha", page_icon="🚿", layout="centered")

ARCHIVO_ESTADO = "estado_ducha.txt"

# Funciones para leer y guardar el estado sin bases de datos raras
def leer_estado():
    if not os.path.exists(ARCHIVO_ESTADO):
        return "libre", "", 0
    with open(ARCHIVO_ESTADO, "r") as f:
        lineas = f.read().splitlines()
        if len(lineas) >= 3:
            return lineas[0], lineas[1], float(lineas[2])
    return "libre", "", 0

def guardar_estado(estado, casa, fin_timestamp):
    with open(ARCHIVO_ESTADO, "w") as f:
        f.write(f"{estado}\n{casa}\n{fin_timestamp}")

# Cargar estado actual
estado, casa, fin_timestamp = leer_estado()
ahora = time.time()

# Si el tiempo ya venció, liberar automáticamente
if estado == "ocupado" and ahora > fin_timestamp:
    estado, casa, fin_timestamp = "libre", "", 0
    guardar_estado(estado, casa, fin_timestamp)

st.title("🚿 Semáforo Ducha")
st.write("Control de presión de agua para las 4 casas")
st.markdown("---")

# Interfaz tipo Semáforo
if estado == "libre":
    # Círculo Verde Grande con HTML personalizado
    st.markdown(
        '<div style="background-color:#2ecc71; width:120px; height:120px; border-radius:50%; margin:20px auto; box-shadow: 0 0 20px #2ecc71;"></div>', 
        unsafe_allow_html=True
    )
    st.subheader("🟢 ESTADO: LIBRE")
    st.write("Puedes ducharte con total presión.")
    
    # Formulario para ocupar
    st.write("### ¿Quién se va a duchar?")
    casa_seleccionada = st.radio(
        "Selecciona tu vivienda:",
        ["Bajo", "Piso 1", "Piso 2", "Ático"],
        index=0,
        horizontal=True
    )
    
    if st.button("Empezar a ducharme (15 min)", type="primary", use_container_width=True):
        tiempo_fin = time.time() + (15 * 60) # 15 minutos
        guardar_estado("ocupado", casa_seleccionada, tiempo_fin)
        st.rerun()

else:
    # Círculo Rojo Grande
    st.markdown(
        '<div style="background-color:#e74c3c; width:120px; height:120px; border-radius:50%; margin:20px auto; box-shadow: 0 0 20px #e74c3c;"></div>', 
        unsafe_allow_html=True
    )
    st.subheader(f"🔴 OCUPADO por: {casa}")
    
    # Calcular tiempo restante
    faltan = int(fin_timestamp - ahora)
    if faltan > 0:
        mins, segs = divmod(faltan, 60)
        st.metric(label="Tiempo restante estimado", value=f"{mins:02d}:{segs:02d}")
    
    if st.button("Ya he terminado (Liberar)", type="secondary", use_container_width=True):
        guardar_estado("libre", "", 0)
        st.rerun()
        
    # Auto-refrescar la pantalla cada 5 segundos para ver si la otra casa ya terminó
    time.sleep(5)
    st.rerun()
