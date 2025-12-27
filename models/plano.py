# models/plano.py
from typing import List, Tuple
from utils.conversor import ConversorCoordenadas
from utils.coordenada import Coordenada
from models.property import Property


class PlanoCatastral:
    def __init__(self, lat_inicial: float, lon_inicial: float):
        self.lat_actual = lat_inicial
        self.lon_actual = lon_inicial
        self.vertices = [(lat_inicial, lon_inicial)]

    def add_segment(self, rumbo: str, distancia: float):
        lat_nuevo, lon_nuevo = ConversorCoordenadas.calcular_destino(
            self.lat_actual, self.lon_actual, rumbo, distancia
        )
        self.vertices.append((lat_nuevo, lon_nuevo))
        self.lat_actual = lat_nuevo
        self.lon_actual = lon_nuevo

    def get_polygon(self) -> List[Tuple[float, float]]:
        coords = self.vertices[:]
        if coords[0] != coords[-1]:
            coords.append(coords[0])
        return coords

    def reboot(self, lat_inicial: float, lon_inicial: float):
        self.lat_actual = lat_inicial
        self.lon_actual = lon_inicial
        self.vertices = [(lat_inicial, lon_inicial)]

    def add_property(self, name: str):
        coords_utm = ConversorCoordenadas.latlon_a_utm(self.get_polygon())
        coords_obj = [Coordenada(x, y) for x, y in coords_utm]
        return Property(name, coords_obj)
