from functools import lru_cache

from pyproj import Transformer


class Coordinates:
    default_zone = 16
    default_hemisphere = 'N'

    def __init__(self, east, north, zone=16, hemisphere='N'):
        if hemisphere not in ['N', 'S']:
            raise ValueError("El hemisferio debe ser 'N' o 'S'")
        self.east = east
        self.north = north
        self.zone = zone or self.default_zone
        self.hemisphere = hemisphere or self.default_hemisphere

    @staticmethod
    def _infer_zone_by_east(east):
        # Aprox. UTM para México si longitud no está disponible
        if east < 0 or east > 1000000:
            raise ValueError("El east debe ser '0' o '1,000,000'")
        zone_utm = int((east / 1000000) * 60) + 1
        return zone_utm


    @staticmethod
    def infer_zone_by_longitude(lon):
        return int((lon + 180) / 6) + 1

    @staticmethod
    @lru_cache(maxsize=16)
    def get_transformer(zone, hemisphere):
        return Transformer.from_crs(
            f"+proj=utm +zone={zone} +{'north' if hemisphere == 'N' else 'south'} +datum=WGS84 +units=m +no_defs",
            "EPSG:4326",
            always_xy=True
        )

    def to_latlon(self):
        transformer = self.get_transformer(self.zone, self.hemisphere)
        lon, lat = transformer.transform(self.east, self.north)
        return lat, lon

    def to_lonlat(self):
        lat, lon = self.to_latlon()
        return lon, lat

    def __repr__(self):
        return f"Coordenada(este={self.east}, norte={self.north}, zona={self.zone}, hemisferio='{self.hemisphere}')"

    def __str__(self):
        return f"UTM: Este {self.east:.2f}, Norte {self.north:.2f}, Zona {self.zone}{self.hemisphere}"

    def __eq__(self, other):
        return (isinstance(other, Coordinates) and
                self.east == other.east and
                self.north == other.north and
                self.zone == other.zone and
                self.hemisphere == other.hemisphere)

    def __hash__(self):
        return hash((self.east, self.north, self.zone, self.hemisphere))

    @staticmethod
    def from_latlon(lat, lon, zone=16, hemisphere='N'):
        zone = zone or Coordinates.infer_zone_by_longitude(lon)
        hemisphere = hemisphere or ('N' if lat >= 0 else 'S')
        transformer = Transformer.from_crs("EPSG:4326",
                                           f"+proj=utm +zone={zone} +{'north' if hemisphere == 'N' else 'south'} +datum=WGS84 +units=m +no_defs",
                                           always_xy=True)
        east, north = transformer.transform(lon, lat)
        return Coordinates(east, north, zone, hemisphere)
