import folium
import random


class Mapa:
    default_name = "map_real_states"
    map_name = None

    def __init__(self):
        self.map = None
        self.realty = []

    @property
    def color_random(self):
        # return "#{:06x}".format(random.randint(0, 0xFFFFFF))
        colores = ['blue', 'green', 'red', 'purple', 'orange', 'darkred']
        return random.choice(colores)

    def add_property(self, realty):
        self.realty.append(realty)
        coords = realty.get_polygon_latlon()

        if coords[0] != coords[-1]:
            coords.append(coords[0])  # Cerrar polígono

        # Centrar mapa si no existe
        if not self.map:
            self.map = folium.Map(location=coords[0], zoom_start=16)

        color = self.color_random()

        # Dibujar el polígono
        folium.Polygon(
            locations=coords,
            popup=realty.name,
            color=color,
            fill=True,
            fill_color=color
        ).add_to(self.map)

        # Área en metros cuadrados
        area_m2 = realty.get_polygon_utm().area

        # Marcar primer punto
        lat, lon = coords[0]
        popup_text = (
            f"<b>{realty.name}</b><br>"
            f"Lat: {lat:.6f}<br>"
            f"Lon: {lon:.6f}<br>"
            f"Área: {area_m2:,.2f} m²<br>"
        )
        if realty.id_catastral:
            popup_text += f"ID Catastral: {realty.id_catastral}<br>"

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(self.map)

    @property
    def save_map(self):
        if not self.map:
            self.map = folium.Map(location=[20.97, -89.62], zoom_start=12)
        if not self.map_name:
            self.map_name = self.default_name
        else:
            self.map_name.replace(" ", "_").lower()

        self.map.save(f"{self.map_name}.html")
        return f"{self.map_name}.html"
