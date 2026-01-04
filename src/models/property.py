from shapely.geometry import Polygon
from src.utils.coordinates import Coordinates

class Property:
    def __init__(self, name: str, coordinates: list[Coordinates], id_catastral: str = None):
        if len(coordinates) < 3:
            raise ValueError(f"El predio '{name}' debe tener al menos 3 coordenadas.")
        self.name = name
        self.coordinates = coordinates
        self.id_catastral = id_catastral

    @property
    def get_polygon_latlon(self):
        return [coord.to_latlon() for coord in self.coordinates]

    @property
    def get_polygon_geojson(self):
        return [coord.to_lonlat() for coord in self.coordinates]

    @property
    def get_polygon_utm(self):
        vertices = [(c.east, c.north) for c in self.coordinates]
        if vertices[0] != vertices[-1]:
            vertices.append(vertices[0])
        return Polygon(vertices)

    @property
    def area_m2(self):
        return self.get_polygon_utm().area

    @property
    def perimeter_m(self):
        return self.get_polygon_utm().length

    @property
    def centroid_latlon(self):
        centroid = self.get_polygon_utm().centroid
        dummy_coord = Coordinates(centroid.x, centroid.y)
        return dummy_coord.to_latlon()
