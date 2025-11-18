import os
import requests
import urllib.parse
import pandas as pd
import streamlit as st

# ==============================
# API KEY DESDE VARIABLE ENTORNO
# ==============================
API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
if not API_KEY:
    st.error("No se encuentra la variable GOOGLE_MAPS_API_KEY. Configúrala antes de ejecutar.")
    st.stop()

# ==============================
# LISTA DE DESTINOS
# ==============================
nombres_centros = [
    "La Almunia de Doña Godina", "CPI San Jorge", "CPI Julio Verne",
    "IES Félix de Azara", "IES Grande Covián", "IES José Manuel Blecua",
    "IES Miralbueno", "CPI Rosales del Canal", "CPI Parque Venecia",
    "CPI Zaragoza Sur", "IES Valdespartera","CPI Valdespartera III",
    "CPI Zaragoza Sur","CPI Soledad Puértolas","CPI Valdespartera III",
    "San Mateo de Gállego", "María de Huerva", "Cuarte de Huerva",
    "San Mateo de Gállego", "Utebo", "Casetas","Zuera", "Cadrete",
    "María de Huerva", "Fuentes de Ebro", "El Burgo de Ebro", "Borja",
    "Bujaraloz", "Alagón", "Calatayud", "Cariñena", "Caspe", "Daroca",
    "Ejea", "Épila", "Gallur", "Illueca", "Maella", "Mallén", "Mequinenza",
    "La Muela", "Pedrola", "Ricla", "Sádaba", "Sástago", "Tarazona",
    "Tauste", "Almudévar", "Huesca", "Sariñena", "Grañén", "Aínsa",
    "Alcolea de Cinca", "Ayerbe", "Barbastro", "Benabarre", "Benasque",
    "Biescas", "Binéfar", "Boltaña", "Castejón de Sos", "Fraga", "Graus",
    "Jaca", "Monzón", "Sabiñánigo", "Tamarite de Litera", "Zaidín",
    "Albarracín", "Alcorisa", "Andorra", "Alcañiz", "Calamocha",
    "Calanda", "Cantavieja", "Cella", "Híjar", "Monreal del Campo",
    "Montalbán", "Mora de Rubielos", "Rubielos de Mora", "San Blás",
    "Teruel", "Utrillas", "Valderrobres", "Ateca", "Belchite", "Borja",
    "Bujaraloz"
]

# ==============================
# FUNCIONES DE LA APP
# ==============================
def construir_url_distance_matrix(origen, destinos, api_key):
    base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    origin_param = urllib.parse.quote(origen)
    destinations_param = urllib.parse.quote("|".join(destinos))

    url = (
        f"{base_url}?origins={origin_param}"
        f"&destinations={destinations_param}"
        f"&mode=driving"
        f"&language=es"
        f"&key={api_key}"
    )
    return url

def obtener_tiempos_y_distancias(origen, nombres_centros, api_key, batch_size=25):
    institutos = [
        {"nombre": nombre, "direccion": f"{nombre}, Aragón, España"}
        for nombre in nombres_centros
    ]

    all_results = []

    for i in range(0, len(institutos), batch_size):
        batch = institutos[i:i + batch_size]
        destinos = [inst["direccion"] for inst in batch]

        url = construir_url_distance_matrix(origen, destinos, api_key)
        resp = requests.get(url)
        data = resp.json()

        if data.get("status") != "OK":
            raise RuntimeError(f"Error en la API: {data}")

        elements = data["rows"][0]["elements"]

        for inst, elem in zip(batch, elements):
            if elem.get("status") != "OK":
                continue
            all_results.append({
                "nombre": inst["nombre"],
                "direccion": inst["direccion"],
                "duration_seconds": elem["duration"]["value"],
                "duration_text": elem["duration"]["text"],
                "distance_meters": elem["distance"]["value"],
                "distance_text": elem["distance"]["text"],
            })

    return all_results

def ordenar_institutos(resultados):
    return sorted(
        resultados,
        key=lambda x: (x["duration_seconds"], x["distance_meters"])
    )

# ==============================
# INTERFAZ STREAMLIT
# ==============================
st.title("Traslados docentes – Ordenado de destinos - JorgeOlleros")
st.markdown("""
Esta app ordena automáticamente tus destinos según:
1. **Tiempo real en coche**  
2. **En caso de empate, distancia (km)**  
""")

origen = st.text_input(
    "Tu domicilio",
    value="C. de Matilde Sangüesa Castañosa, 53, 50015 Zaragoza, España"
)

destinos_text = st.text_area(
    "Destinos (uno por línea)",
    value="\n".join(nombres_centros),
    height=300
)

if st.button("Calcular"):
    destinos_lista = [d.strip() for d in destinos_text.splitlines() if d.strip()]
    with st.spinner("Calculando distancias..."):
        resultados = obtener_tiempos_y_distancias(origen, destinos_lista, API_KEY)
        ordenados = ordenar_institutos(resultados)
        
        df = pd.DataFrame(ordenados)
        df_vista = df[["nombre", "duration_text", "distance_text", "direccion"]]
        df_vista.columns = ["Destino", "Tiempo", "Distancia", "Dirección"]

        df_vista.insert(0, "#", range(1, len(df_vista) + 1))

        st.subheader("Resultados")
        st.dataframe(df_vista, use_container_width=True)

        csv = df_vista.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Descargar CSV",
            csv,
            "destinos_ordenados.csv",
            "text/csv"
        )
