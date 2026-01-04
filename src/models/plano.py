from typing import List, Tuple
from src.utils.convert import Convert
from src.utils.coordinates import Coordinates
from src.models.property import Property


class PlanoCatastral:
    def __init__(self, lat_initial: float, lon_initial: float):
        self.lat_current = lat_initial
        self.lon_current = lon_initial
        self.vertices = [(lat_initial, lon_initial)]

    def add_segment(self, rumbo: str, distance: float):
        lat_new, lon_new = Convert.calculate_destination(
            self.lat_current, self.lon_current, rumbo, distance
        )
        self.vertices.append((lat_new, lon_new))
        self.lat_current = lat_new
        self.lon_current = lon_new

    def get_polygon(self) -> List[Tuple[float, float]]:
        coords = self.vertices[:]
        if coords[0] != coords[-1]:
            coords.append(coords[0])
        return coords

    def reboot(self, lat_initial: float, lon_initial: float):
        self.lat_current = lat_initial
        self.lon_current = lon_initial
        self.vertices = [(lat_initial, lon_initial)]

    def add_property(self, name: str):
        coords_utm = Convert.latlon_to_utm(self.get_polygon())
        coords_obj = [Coordinates(x, y) for x, y in coords_utm]
        return Property(name, coords_obj)
