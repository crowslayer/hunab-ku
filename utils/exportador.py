import json
import os
from shapely.geometry import Polygon, mapping

class ExportadorGeoJSON:
    @staticmethod
    def export(predios, archivo_salida="predios.geojson"):
        features = []
        for predio in predios:
            coords = predio.get_polygon_geojson()

            if not coords or len(coords) < 3:
                raise ValueError(
                    f"El predio '{predio.name}' no tiene suficientes coordenadas para formar un polígono válido.")

            if coords[0] != coords[-1]:
                coords.append(coords[0])  # Cerrar polígono

            poly = Polygon(coords)
            features.append({
                "type": "Feature",
                "properties": {"nombre": predio.name},
                "geometry": mapping(poly)
            })

        geojson = {
            "type": "FeatureCollection",
            "features": features,
            "crs": {
                "type": "name",
                "properties": {"name": "EPSG:4326"}
            }
        }

        if archivo_salida:
            carpeta = os.path.dirname(archivo_salida)
            if carpeta:
                os.makedirs(carpeta, exist_ok=True)
            with open(archivo_salida, "w", encoding="utf-8") as f:
                json.dump(geojson, f, ensure_ascii=False, indent=2)
        return geojson