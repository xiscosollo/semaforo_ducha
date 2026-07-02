import streamlit as st
import time
import os
import uuid

# Configuración limpia y compacta
st.set_page_config(page_title="Ducha", page_icon="🚿", layout="centered")

ARCHIVO_ESTADO = "estado_ducha.txt"

# Generar un ID único para este navegador si no existe
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = str(uuid.uuid4())

def leer_estado():
    if not os.path.exists(ARCHIVO_ESTADO):
        return "libre", "", 0, ""
    with open(ARCHIVO_ESTADO, "r") as f:
        lineas = f.read().splitlines()
        if len(lineas) >= 4:
            return lineas[0], lineas[1], float(lineas[2]), lineas[3]
    return "libre", "", 0, ""

def guardar_estado(estado, casa, fin_timestamp, id_usuario):
    with open(ARCHIVO_ESTADO, "w") as f:
        f.write(f"{estado}\n{casa}\n{fin_timestamp}\n{id_usuario}")

# Lógica de inicio
estado, casa_ocupante, fin_ts, id_ocupante = leer_estado()
ahora = time.time()

# Auto-liberar si pasó el tiempo
if estado == "ocupado" and ahora > fin_ts:
    estado = "libre"
    guardar_estado("libre", "", 0, "")

st.title("🚿 Ducha")
st.markdown("---")

if estado == "libre":
    st.success("### 🟢 ESTADO: LIBRE")
    st.write("Puedes ducharte con total presión.")
    
    st.write("### ¿Quién se va a duchar?")
    piso = st.radio("Selecciona tu vivienda:", ["Bajo", "Piso 1", "Piso 2", "Ático"], horizontal=True, label_visibility="collapsed")
    
    if st.button("EMPEZAR A DUCHARSE", type="primary", use_container_width=True):
        guardar_estado("ocupado", piso, ahora + 900, st.session_state['user_id'])
        st.rerun()
else:
    st.error(f"### 🔴 OCUPADO POR: {casa_ocupante.upper()}")
    
    # Temporizador
    faltan = int(fin_ts - ahora)
    if faltan > 0:
        mins, segs = divmod(faltan, 60)
        st.metric("Tiempo restante estimado", f"{mins:02d}:{segs:02d}")
    
    # Bloqueo de seguridad: Solo el dueño de la sesión puede terminar antes de tiempo
    if st.session_state['user_id'] == id_ocupante:
        if st.button("TERMINAR (LIBERAR AGUA)", type="secondary", use_container_width=True):
            guardar_estado("libre", "", 0, "")
            st.rerun()
    else:
        st.info("Solo el vecino que inició la ducha puede usar el botón 'Terminar'. El sistema se liberará solo cuando el contador llegue a cero.")

    # Auto-refresco en segundo plano cada 5 segundos para actualizar el tiempo o el estado
    time.sleep(5)
    st.rerun()
