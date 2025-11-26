import urllib.parse
import requests

def construir_url_distance_matrix(origen, destinos, api_key, mode):
    base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    origin_param = urllib.parse.quote(origen)
    destinations_param = urllib.parse.quote("|".join(destinos))

    url = (
        f"{base_url}?origins={origin_param}"
        f"&destinations={destinations_param}"
        f"&mode={mode}"
        f"&language=es"
        f"&key={api_key}"
    )
    return url

def obtener_tiempos_y_distancias(origen, nombres_centros, api_key, ubicacion_suffix, mode, batch_size=25):
    institutos = [
        {"nombre": nombre, "direccion": f"{nombre}{ubicacion_suffix}"}
        for nombre in nombres_centros
    ]

    all_results = []

    for i in range(0, len(institutos), batch_size):
        batch = institutos[i:i + batch_size]
        destinos = [inst["direccion"] for inst in batch]

        url = construir_url_distance_matrix(origen, destinos, api_key, mode)
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