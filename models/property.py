# models/property.py

from shapely.geometry import Polygon
from utils.coordenada import Coordenada

class Property:
    def __init__(self, name: str, coordinates: list[Coordenada], id_catastral: str = None):
        if len(coordinates) < 3:
            raise ValueError(f"El predio '{name}' debe tener al menos 3 coordenadas.")
        self.name = name
        self.coordinates = coordinates
        self.id_catastral = id_catastral

    def get_polygon_latlon(self):
        return [coord.to_latlon() for coord in self.coordinates]

    def get_polygon_geojson(self):
        return [coord.to_lonlat() for coord in self.coordinates]

    def get_polygon_utm(self):
        puntos = [(c.este, c.norte) for c in self.coordinates]
        if puntos[0] != puntos[-1]:
            puntos.append(puntos[0])
        return Polygon(puntos)

    @property
    def area_m2(self):
        return self.get_polygon_utm().area

    @property
    def perimeter_m(self):
        return self.get_polygon_utm().length

    @property
    def centroide_latlon(self):
        centroide = self.get_polygon_utm().centroid
        dummy_coord = Coordenada(centroide.x, centroide.y)
        return dummy_coord.to_latlon()
