import folium
import random
from shapely.geometry import Polygon

class Mapa:
    def __init__(self):
        self.mapa = None
        self.properties = []

    def color_random(self):
        # return "#{:06x}".format(random.randint(0, 0xFFFFFF))
        colores = ['blue', 'green', 'red', 'purple', 'orange', 'darkred']
        return random.choice(colores)

    def add_property(self, property):
        self.properties.append(property)
        coords = property.get_polygon_latlon()

        if coords[0] != coords[-1]:
            coords.append(coords[0])  # Cerrar polígono

        # Centrar mapa si no existe
        if not self.mapa:
            self.mapa = folium.Map(location=coords[0], zoom_start=16)

        color = self.color_random()

        # Dibujar el polígono
        folium.Polygon(
            locations=coords,
            popup=property.name,
            color=color,
            fill=True,
            fill_color=color
        ).add_to(self.mapa)

        # Área en metros cuadrados
        area_m2 = property.get_polygon_utm().area

        # Marcar primer punto
        lat, lon = coords[0]
        popup_text = (
            f"<b>{property.name}</b><br>"
            f"Lat: {lat:.6f}<br>"
            f"Lon: {lon:.6f}<br>"
            f"Área: {area_m2:,.2f} m²<br>"
        )
        if property.id_catastral:
            popup_text += f"ID Catastral: {property.id_catastral}<br>"

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(self.mapa)

    def save_map(self):
        if not self.mapa:
            self.mapa = folium.Map(location=[20.97, -89.62], zoom_start=12)
        self.mapa.save("mapa_predios.html")
