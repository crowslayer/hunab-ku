import json
import os
from shapely.geometry import Polygon, mapping

class ExportGeoJSON:
    @staticmethod
    def export(properties, filename_output="predios.geojson"):
        features = []
        for property in properties:
            coords = property.get_polygon_geojson()

            if not coords or len(coords) < 3:
                raise ValueError(
                    f"El predio '{property.name}' no tiene suficientes coordenadas para formar un polígono válido.")

            if coords[0] != coords[-1]:
                coords.append(coords[0])  # Cerrar polígono

            poly = Polygon(coords)
            features.append({
                "type": "Feature",
                "properties": {"nombre": property.name},
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

        if filename_output:
            carpeta = os.path.dirname(filename_output)
            if carpeta:
                os.makedirs(carpeta, exist_ok=True)
            with open(filename_output, "w", encoding="utf-8") as f:
                json.dump(geojson, f, ensure_ascii=False, indent=2)
        return filename_output