import re
import math
from pyproj import Transformer

class Convert:
    @staticmethod
    def dms_to_decimal(dms_str):
        """
        Convierte una coordenada en formato DMS (ej. 'N 20° 58' 35.2"') a decimal.
        """
        pattern = r"""([NSWE])\s*
                      (\d+)[°\s]*
                      (\d+)[\'\s]*
                      ([\d.,]+)\"?"""
        match = re.match(pattern, dms_str.strip(), re.VERBOSE)
        if not match:
            raise ValueError(f"Formato DMS inválido: {dms_str}")

        dir_, degrees, minutes, seconds = match.groups()
        seconds = seconds.replace(',', '.')  # Normaliza coma decimal

        decimal = float(degrees) + float(minutes) / 60 + float(seconds) / 3600
        return -decimal if dir_ in ['S', 'W'] else decimal

    @staticmethod
    def utm_to_latlon(coords_utm, epsg=32616):
        """
        Convierte una lista de coordenadas UTM [(x, y), ...] a lat/lon usando el EPSG indicado (default: 32616 para Yucatán).
        """
        transformer = Transformer.from_crs(f"EPSG:{epsg}", "EPSG:4326", always_xy=True)
        return [transformer.transform(x, y) for x, y in coords_utm]

    @staticmethod
    def latlon_to_utm(coords_latlon, epsg=32616):
        """
        Convierte una lista de coordenadas (lat, lon) a UTM con EPSG indicado.
        """
        transformer = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)
        return [transformer.transform(lon, lat) for lat, lon in coords_latlon]

    @staticmethod
    def rumbo_to_azimuth(rumbo_str):
        """
        Convierte un rumbo tipo 'N 03°52'42.68'' E' a ángulo azimutal en grados.
        """
        pattern = r"""([NS])\s*
                          (\d+)[°\s]*
                          (\d+)[\'\s]*
                          ([\d.,]+)(?:''|\"|”)?\s*
                          ([EW])"""
        match = re.match(pattern, rumbo_str.strip(), re.VERBOSE | re.IGNORECASE)
        if not match:
            raise ValueError(f"Formato de rumbo inválido: {rumbo_str}")

        ns, degrees, minutes, seconds, ew = match.groups()
        seconds = seconds.replace(',', '.')

        base_angle = float(degrees) + float(minutes) / 60 + float(seconds) / 3600

        if ns.upper() == 'N' and ew.upper() == 'E':
            azimuth = base_angle
        elif ns.upper() == 'S' and ew.upper() == 'E':
            azimuth = 180 - base_angle
        elif ns.upper() == 'S' and ew.upper() == 'W':
            azimuth = 180 + base_angle
        elif ns.upper() == 'N' and ew.upper() == 'W':
            azimuth = 360 - base_angle
        else:
            raise ValueError("Direcciones cardinales inválidas")

        return azimuth

    @staticmethod
    def calculate_destination(lat0, lon0, rumbo_str, distance_meters):
        """
        A partir de un punto (lat/lon), rumbo y distancia, calcula la nueva coordenada (lat, lon).
        """
        azimuth = Convert.rumbo_to_azimuth(rumbo_str)
        r = 6378137  # Radio de la Tierra en metros (WGS84)
        az_rad = math.radians(azimuth)

        lat0_rad = math.radians(lat0)
        lon0_rad = math.radians(lon0)

        delta = distance_meters / r

        lat1_rad = math.asin(
            math.sin(lat0_rad) * math.cos(delta) +
            math.cos(lat0_rad) * math.sin(delta) * math.cos(az_rad)
        )

        lon1_rad = lon0_rad + math.atan2(
            math.sin(az_rad) * math.sin(delta) * math.cos(lat0_rad),
            math.cos(delta) - math.sin(lat0_rad) * math.sin(lat1_rad)
        )

        lat1 = math.degrees(lat1_rad)
        lon1 = math.degrees(lon1_rad)

        return lat1, lon1

    @staticmethod
    def decimal_to_dms(decimal, tipo='lat'):
        degrees = int(abs(decimal))
        minutes = int((abs(decimal) - degrees) * 60)
        seconds = (abs(decimal) - degrees - minutes / 60) * 3600

        direction = ''
        if tipo == 'lat':
            direction = 'N' if decimal >= 0 else 'S'
        elif tipo == 'lon':
            direction = 'E' if decimal >= 0 else 'W'
        return f"{direction} {degrees}° {minutes}' {seconds:.2f}\""
