import re
import math
from pyproj import Transformer

class ConversorCoordenadas:
    @staticmethod
    def dms_a_decimal(dms_str):
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

        dir_, grados, minutos, segundos = match.groups()
        segundos = segundos.replace(',', '.')  # Normaliza coma decimal

        decimal = float(grados) + float(minutos) / 60 + float(segundos) / 3600
        return -decimal if dir_ in ['S', 'W'] else decimal

    @staticmethod
    def utm_a_latlon(coords_utm, epsg=32616):
        """
        Convierte una lista de coordenadas UTM [(x, y), ...] a lat/lon usando el EPSG indicado (default: 32616 para Yucatán).
        """
        transformer = Transformer.from_crs(f"EPSG:{epsg}", "EPSG:4326", always_xy=True)
        return [transformer.transform(x, y) for x, y in coords_utm]

    @staticmethod
    def latlon_a_utm(coords_latlon, epsg=32616):
        """
        Convierte una lista de coordenadas (lat, lon) a UTM con EPSG indicado.
        """
        transformer = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)
        return [transformer.transform(lon, lat) for lat, lon in coords_latlon]

    @staticmethod
    def rumbo_a_azimut(rumbo_str):
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

        ns, grados, minutos, segundos, ew = match.groups()
        segundos = segundos.replace(',', '.')

        base_angle = float(grados) + float(minutos) / 60 + float(segundos) / 3600

        if ns.upper() == 'N' and ew.upper() == 'E':
            azimut = base_angle
        elif ns.upper() == 'S' and ew.upper() == 'E':
            azimut = 180 - base_angle
        elif ns.upper() == 'S' and ew.upper() == 'W':
            azimut = 180 + base_angle
        elif ns.upper() == 'N' and ew.upper() == 'W':
            azimut = 360 - base_angle
        else:
            raise ValueError("Direcciones cardinales inválidas")

        return azimut

    @staticmethod
    def calcular_destino(lat0, lon0, rumbo_str, distancia_metros):
        """
        A partir de un punto (lat/lon), rumbo y distancia, calcula la nueva coordenada (lat, lon).
        """
        azimut = ConversorCoordenadas.rumbo_a_azimut(rumbo_str)
        R = 6378137  # Radio de la Tierra en metros (WGS84)
        az_rad = math.radians(azimut)

        lat0_rad = math.radians(lat0)
        lon0_rad = math.radians(lon0)

        delta = distancia_metros / R

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
    def decimal_a_dms(decimal, tipo='lat'):
        grados = int(abs(decimal))
        minutos = int((abs(decimal) - grados) * 60)
        segundos = (abs(decimal) - grados - minutos / 60) * 3600

        direccion = ''
        if tipo == 'lat':
            direccion = 'N' if decimal >= 0 else 'S'
        elif tipo == 'lon':
            direccion = 'E' if decimal >= 0 else 'W'
        return f"{direccion} {grados}° {minutos}' {segundos:.2f}\""
