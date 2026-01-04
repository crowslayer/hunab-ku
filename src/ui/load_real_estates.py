import ttkbootstrap as tb
import tkinter as tk

from ttkbootstrap.widgets.scrolled import ScrolledText
from src.models.mapa import Mapa
from tkinter import messagebox
from src.models.property import Property
from src.utils.coordinates import Coordinates
from src.utils.export_geojson import ExportGeoJSON
from src.models.plano import PlanoCatastral
from src.utils.render_browser import RenderInBrowser


class LoadRealEstates(tb.Frame):
    default_name = 'mapa_predios'
    map_name = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.properties = []
        self.map = Mapa()
        self.pack()
        self.create_components()

    def create_components(self):
        tb.Label(self, text="Ingrese los datos del predio:",
                  font=("Segoe UI", 12, "bold")).pack(pady=(10, 5))

        self.input = ScrolledText(self, height=8, width=80, wrap='word', font=("Segoe UI", 10))
        self.input.pack(pady=5)
        #
        ejemplo = ("Ejemplo de formato:\n"
                   "Predio1, 507000 2200000; 507100 2200000; 507100 2200100; 507000 2200100\n"
                   "Predio2, 507200 2200200; 507300 2200200; 507300 2200300; 507200 2200300")
        tb.Label(self, text=ejemplo, foreground="gray", font=("Segoe UI", 9)).pack(pady=(0, 10))

        self.frame_buttons = tb.Frame(self)
        self.frame_buttons.pack(pady=10)

        self.button_process = tb.Button(self.frame_buttons, text="Procesar predios", command=self.process_input)
        self.button_process.grid(row=0, column=0, padx=10)

        self.button_map = tb.Button(self.frame_buttons, text="Mostrar mapa", command=self.show_map)
        self.button_map.grid(row=0, column=1, padx=10)

        self.button_export = tb.Button(self.frame_buttons, text="Exportar a GeoJSON", command=self.export_geojson)
        self.button_export.grid(row=0, column=2, padx=10)

        tb.Label(self, text="Predios procesados:",
                  font=("Segoe UI", 11, "bold")).pack(pady=(10, 5))

        self.property_list = tk.Listbox(self, height=6, font=("Segoe UI", 10))
        self.property_list.pack(pady=5, fill="x", padx=20)

    def process_input(self):
        text = self.input.get("1.0", 'end').strip()
        if not text:
            messagebox.showwarning("Aviso", "No se ingresaron coordenadas.")
            return

        try:
            self.properties.clear()
            self.property_list.delete(0, 'end')
            self.map = Mapa()

            for line in text.split("\n"):
                if not line.strip():
                    continue
                name, coords_str = line.split(",", 1)
                name = name.strip()
                coords_raw = coords_str.strip().split(";")

                coords = []
                for par in coords_raw:
                    este, norte = map(float, par.strip().split())
                    coords.append(Coordinates(este, norte))

                realty = Property(name, coords)
                self.properties.append(realty)
                self.map.add_property(realty)
                self.property_list.insert('end', f"{realty.name} ({len(coords)} vértices)")

            messagebox.showinfo("Éxito", f"{len(self.properties)} predio(s) procesado(s) correctamente.")

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}", icon="error")

    def show_map(self):
        if not self.properties:
            messagebox.showwarning("Aviso", "No hay predios procesados.", icon="warning")
            return
        map_name = self.map.save_map()
        RenderInBrowser.show(map_name)

        messagebox.showinfo("Mapa", "Mapa generado y abierto en el navegador.")


    def export_geojson(self):
        if not self.properties:
            messagebox.showwarning("Aviso", "No hay predios para exportar.", icon="error")
            return
        json_name = ExportGeoJSON.export(self.properties)
        RenderInBrowser.show(json_name)
        messagebox.showinfo("GeoJSON", "Archivo 'predios.geojson' generado exitosamente.")

    def load_from_plane(self):
        texto = self.input.get("1.0", 'end').strip()
        if not texto:
            messagebox.showwarning("Aviso", "No se ingresaron datos del plano.", icon="error")
            return

        try:
            # Primer punto fijo (reemplazar con el punto base de tu plano)
            lat0 = 20.967000
            lon0 = -89.623000

            plano = PlanoCatastral(lat0, lon0)
            for linea in texto.split("\n"):
                if not linea.strip():
                    continue
                partes = linea.split(",")
                rumbo = partes[2].strip()
                distancia = float(partes[3].strip())
                plano.add_segment(rumbo, distancia)

            coords_latlon = plano.get_polygon()

            # Crear coordenadas en objeto Coordenada
            coords_obj = [Coordinates(east=0, north=0) for _ in coords_latlon]  # placeholder

            # Sobrescribimos to_latlon() para este uso
            for i, (lat, lon) in enumerate(coords_latlon):
                coords_obj[i].to_latlon = lambda lat=lat, lon=lon: (lat, lon)

            real_state = Property("Predio desde plano", coords_obj)
            self.properties.append(real_state)
            self.map.add_property(real_state)

            messagebox.showinfo("Éxito", "Plano cargado correctamente.")

        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar plano: {str(e)}")
