import os
import pandas as pd
import streamlit as st

from core import obtener_tiempos_y_distancias, ordenar_institutos


import streamlit.components.v1 as components

# ==============================
# CONTADOR DE VISITAS (STATCOUNTER)
# ==============================
ga_code = """
<!-- Default Statcounter code for Concurso Traslados
https://concursotraslados.streamlit.app/ -->
<script type="text/javascript">
var sc_project=13187725; 
var sc_invisible=1; 
var sc_security="f04b0a7d"; 
</script>
<script type="text/javascript"
src="https://www.statcounter.com/counter/counter.js" async></script>
<noscript><div class="statcounter"><a title="Web Analytics Made Easy -
Statcounter" href="https://statcounter.com/" target="_blank"><img
class="statcounter" src="https://c.statcounter.com/13187725/0/f04b0a7d/1/"
alt="Web Analytics Made Easy - Statcounter"
referrerPolicy="no-referrer-when-downgrade"></a></div></noscript>
<!-- End of Statcounter Code -->
"""

components.html(ga_code, height=0, width=0)

# ==============================
# CONTADOR DE VISITAS (FICHERO LOCAL)
# ==============================
COUNTER_FILE = "visitas.txt"


def leer_contador():
    """Lee el número de visitas desde el fichero. Si no existe, devuelve 0."""
    try:
        if not os.path.exists(COUNTER_FILE):
            return 0
        with open(COUNTER_FILE, "r", encoding="utf-8") as f:
            contenido = f.read().strip()
            if not contenido:
                return 0
            return int(contenido)
    except Exception as e:
        print("Error leyendo contador:", e)
        return 0


def incrementar_contador():
    """Incrementa el contador en 1 y lo guarda en el fichero. Devuelve el nuevo valor."""
    valor = leer_contador()
    valor += 1
    try:
        with open(COUNTER_FILE, "w", encoding="utf-8") as f:
            f.write(str(valor))
    except Exception as e:
        print("Error escribiendo contador:", e)
    return valor

# ==============================
# API KEY DESDE VARIABLE ENTORNO
# ==============================
API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
if not API_KEY:
    st.error("No se encuentra la variable GOOGLE_MAPS_API_KEY. Configúrala antes de ejecutar.")
    st.stop()

# ==============================
# LISTA DE DESTINOS POR DEFECTO
# ==============================
nombres_centros = [
    "Calatayud",
    "CPI San Jorge",
    "Rubielos de Mora"
    # Añade aquí los que quieras por defecto: Zaragoza, Huesca...
]

# ==============================
# LISTA DE COMUNIDADES AUTÓNOMAS
# ==============================
COMUNIDADES = [
    "Andalucía", "Aragón", "Asturias", "Baleares", "Canarias", "Cantabria",
    "Castilla-La Mancha", "Castilla y León", "Cataluña", "Comunidad Valenciana",
    "Extremadura", "Galicia", "La Rioja", "Madrid", "Murcia", "Navarra",
    "País Vasco", "Ceuta", "Melilla"
]

# Mapeo de modo “humano” → modo API Google
MAPA_MODOS = {
    "Coche": "driving",
    "Andando": "walking",
    "Bicicleta": "bicycling",
}

# ==============================
# CONTABILIZAR VISITA (SOLO UNA VEZ POR SESIÓN)
# ==============================
if "visita_contabilizada" not in st.session_state:
    total_visitas = incrementar_contador()
    st.session_state["visita_contabilizada"] = True
else:
    total_visitas = leer_contador()
# Ojo: NO mostramos total_visitas en la interfaz. Solo se usa visitas.txt.

# ==============================
# INTERFAZ STREAMLIT
# ==============================
st.title("Concurso de traslados – Ordenador de destinos")

st.markdown("""
Esta app ordena automáticamente tus destinos según:

1. **Tiempo real de desplazamiento**  
2. **En caso de empate, distancia (km)**  
3. Permite elegir **ámbito (nacional / CCAA)** y **tipo de transporte**.  
""")

# Origen
origen = st.text_input(
    "Escribe aquí la dirección de tu domicilio o punto de origen:",
    value="C. de Matilde Sangüesa Castañosa, 53, Zaragoza, España"
)

# Destinos
destinos_text = st.text_area(
    "Escribe aquí los centros educativos/municipios a ordenar (uno por línea, ver ejemplos):",
    value="\n".join(nombres_centros),
    height=300
)

# Ámbito
ambito = st.selectbox(
    "Ámbito de la convocatoria:",
    ["Nacional (toda España)", "Comunidad autónoma"]
)

if ambito == "Comunidad autónoma":
    comunidad = st.selectbox("Elige la comunidad autónoma:", COMUNIDADES)
    ubicacion_suffix = f", {comunidad}, España"
else:
    comunidad = None
    ubicacion_suffix = ", España"

# Modo de transporte
modo_transporte = st.selectbox(
    "Elige el tipo de transporte:",
    ["Coche", "Andando", "Bicicleta"]
)
mode = MAPA_MODOS[modo_transporte]


# ==============================
# BOTÓN PRINCIPAL
# ==============================
if st.button("Calcular"):
    destinos_lista = [d.strip() for d in destinos_text.splitlines() if d.strip()]

    if not origen.strip():
        st.error("Debes introducir un origen.")
    elif not destinos_lista:
        st.error("Debes introducir al menos un destino.")
    else:
        # Debug opcional en terminal:
        # print("Origen:", origen)
        # print("Destinos:", destinos_lista)
        # print("Sufijo ubicación:", ubicacion_suffix)
        # print("Modo transporte:", mode)

        with st.spinner("Calculando distancias..."):
            try:
                resultados = obtener_tiempos_y_distancias(
                    origen=origen,
                    nombres_centros=destinos_lista,
                    api_key=API_KEY,
                    ubicacion_suffix=ubicacion_suffix,
                    mode=mode,
                )
                ordenados = ordenar_institutos(resultados)

                if not ordenados:
                    st.warning("No se ha podido obtener información de ningún destino.")
                else:
                    df = pd.DataFrame(ordenados)
                    df_vista = df[["nombre", "duration_text", "distance_text", "direccion"]]
                    df_vista.columns = ["Destino", "Tiempo", "Distancia", "Dirección"]
                    df_vista.insert(0, "#", range(1, len(df_vista) + 1))

                    st.subheader("Aquí tienes los resultados. Suerte, yo no te voy a llenar el tanque...")
                    st.dataframe(df_vista, use_container_width=True)

                    csv = df_vista.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "Descargar CSV",
                        csv,
                        "destinos_ordenados_jorgeodm.csv",
                        "text/csv"
                    )
            except Exception as e:
                st.error(f"Se ha producido un error al calcular distancias: {e}")
