from functools import lru_cache

from pyproj import Transformer


class Coordenada:
    def __init__(self, este, norte, zona=16, hemisferio='N'):
        if hemisferio not in ['N', 'S']:
            raise ValueError("El hemisferio debe ser 'N' o 'S'")
        self.este = este
        self.norte = norte
        self.zona = zona or self._inferir_zona_por_este(este)
        self.hemisferio = hemisferio

    @staticmethod
    def _inferir_zona_por_este(este):
        # Aprox. UTM para México si longitud no está disponible
        return 16

    @staticmethod
    def inferir_zona_por_longitud(lon):
        return int((lon + 180) / 6) + 1

    @staticmethod
    @lru_cache(maxsize=16)
    def get_transformer(zona, hemisferio):
        return Transformer.from_crs(
            f"+proj=utm +zone={zona} +{'north' if hemisferio == 'N' else 'south'} +datum=WGS84 +units=m +no_defs",
            "EPSG:4326",
            always_xy=True
        )

    def to_latlon(self):
        transformer = self.get_transformer(self.zona, self.hemisferio)
        lon, lat = transformer.transform(self.este, self.norte)
        return lat, lon

    def to_lonlat(self):
        lat, lon = self.to_latlon()
        return lon, lat

    def __repr__(self):
        return f"Coordenada(este={self.este}, norte={self.norte}, zona={self.zona}, hemisferio='{self.hemisferio}')"

    def __str__(self):
        return f"UTM: Este {self.este:.2f}, Norte {self.norte:.2f}, Zona {self.zona}{self.hemisferio}"

    def __eq__(self, other):
        return (isinstance(other, Coordenada) and
                self.este == other.este and
                self.norte == other.norte and
                self.zona == other.zona and
                self.hemisferio == other.hemisferio)

    def __hash__(self):
        return hash((self.este, self.norte, self.zona, self.hemisferio))

    @staticmethod
    def from_latlon(lat, lon, zona=16, hemisferio='N'):
        zona = zona or Coordenada.inferir_zona_por_longitud(lon)
        hemisferio = hemisferio or ('N' if lat >= 0 else 'S')
        transformer = Transformer.from_crs("EPSG:4326",
                                           f"+proj=utm +zone={zona} +{'north' if hemisferio == 'N' else 'south'} +datum=WGS84 +units=m +no_defs",
                                           always_xy=True)
        este, norte = transformer.transform(lon, lat)
        return Coordenada(este, norte, zona, hemisferio)
