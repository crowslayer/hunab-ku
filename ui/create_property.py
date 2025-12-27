import ttkbootstrap as tb
from tkinter import messagebox

from utils.exportador import ExportadorGeoJSON
from models.mapa import Mapa
from utils.coordenada import Coordenada
from models.property import Property


class CreateProperty(tb.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.rows = []
        self.map = Mapa()

        # Título
        tb.Label(self, text="Ingrese los datos del predio:",
                 font=("Segoe UI", 12, "bold")).pack(pady=(10, 5))

        # Campo: nombre del predio
        name_frame = tb.Frame(self)
        name_frame.pack(pady=5)
        tb.Label(name_frame, text="Nombre del predio:").pack(side="left")
        self.name_entry = tb.Entry(name_frame, width=30, style='primary.TEntry')
        self.name_entry.pack(side="left", padx=10)

        # Tipo de coordenada
        type_frame = tb.Frame(self)
        type_frame.pack(pady=(5, 0))
        tb.Label(type_frame, text="Tipo de coordenada:").pack(side="left")

        self.tipo_var = tb.StringVar(value="UTM")
        self.type_combo = tb.Combobox(type_frame, textvariable=self.tipo_var,
                                      values=["UTM", "Decimal", "DMS"],
                                      state="readonly", width=15, style='success.TCombobox')
        self.type_combo.pack(side="left", padx=10)
        self.type_combo.bind("<<ComboboxSelected>>", self._update_state_combo)

        # Estado (zona UTM)
        zona_frame = tb.Frame(self)
        zona_frame.pack(pady=(5, 10))
        tb.Label(zona_frame, text="Estado (para zona UTM):").pack(side="left")

        self.state_var = tb.StringVar()
        self.state_combo = tb.Combobox(zona_frame, textvariable=self.state_var,
                                       values=[
                                            "Baja California (Zona 11)",
                                            "Sonora, Sinaloa (Zona 12)",
                                            "Chihuahua, Durango (Zona 13)",
                                            "Zacatecas, San Luis Potosí (Zona 14)",
                                            "Jalisco, Guanajuato, Querétaro (Zona 14)",
                                            "CDMX, Puebla, Veracruz (Zona 15)",
                                            "Oaxaca, Chiapas (Zona 16)",
                                            "Yucatán, Quintana Roo, Campeche (Zona 16/17)"
                                        ],
                                       state="readonly", width=40, style='primary.TCombobox')
        self.state_combo.pack(side="left", padx=10)

        # Contenedor de coordenadas
        self.coord_frame = tb.Frame(self)
        self.coord_frame.pack(pady=10)

        # Encabezados
        self._crete_headers()

        self.add_row()

        # Botones
        btn_frame = tb.Frame(self)
        btn_frame.pack(pady=10)

        tb.Button(btn_frame, text="Agregar Vértice", command=self.add_row).pack(side="left", padx=10)
        tb.Button(btn_frame, text="Crear predio y mostrar mapa", command=self.create_property).pack(side="left", padx=10)
        tb.Button(btn_frame, text="Eliminar último vértice", command=self.remove_last_row).pack(side="left", padx=10)

    def add_row(self):
        row_idx = len(self.rows) + 1
        y_entry = tb.Entry(self.coord_frame, width=15)
        x_entry = tb.Entry(self.coord_frame, width=15)

        tb.Label(self.coord_frame, text=row_idx).grid(row=row_idx, column=0, padx=5, pady=2)
        y_entry.grid(row=row_idx, column=1, padx=5, pady=2)
        x_entry.grid(row=row_idx, column=2, padx=5, pady=2)

        self.rows.append((x_entry, y_entry))

    def remove_last_row(self):
        if self.rows:
            x_entry, y_entry = self.rows.pop()
            x_entry.destroy()
            y_entry.destroy()
            row_idx = len(self.rows) + 1
            label = self.coord_frame.grid_slaves(row=row_idx, column=0)
            if label:
                label[0].destroy()

    def _reset_entrys(self):
        for x_entry, y_entry in self.rows:
            x_entry.configure(background="white")
            y_entry.configure(background="white")

    def _crete_headers(self):
        headers = ["V", "Y (Norte)", "X (Este)"]
        for i, h in enumerate(headers):
            tb.Label(self.coord_frame, text=h).grid(row=0, column=i, padx=5, pady=5)

    def _update_state_combo(self, event=None):
        if self.tipo_var.get() == "UTM":
            self.state_combo.configure(state="readonly")
        else:
            self.state_combo.set("")
            self.state_combo.configure(state="disabled")

    def _zona_from_state(self):
        state = self.state_var.get()
        if "Zona 11" in state:
            return 11
        elif "Zona 12" in state:
            return 12
        elif "Zona 13" in state:
            return 13
        elif "Zona 14" in state:
            return 14
        elif "Zona 15" in state:
            return 15
        elif "Zona 16" in state:
            return 16
        elif "Zona 17" in state:
            return 17
        return 16  # default

    def create_property(self):
        self._reset_entrys()
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Debe ingresar un nombre para el predio.")
            return

        tipo = self.tipo_var.get()
        zona = self._zona_from_state() if tipo == "UTM" else 16  # default para Decimal y DMS
        coordinates = []

        for idx, (x_entry, y_entry) in enumerate(self.rows, start=1):
            try:
                x = float(x_entry.get().replace(",", ""))
                y = float(y_entry.get().replace(",", ""))
                coord = Coordenada(x, y, zona=zona)
                coordinates.append(coord)
            except ValueError:
                x_entry.configure(background="#ffcdd2")  # rojo claro
                y_entry.configure(background="#ffcdd2")
                messagebox.showerror("Error", f"Coordenadas inválidas en el vértice {idx}.")
                return

        if len(coordinates) < 3:
            messagebox.showerror("Error", "Debe haber al menos 3 coordenadas.")
            return

        try:
            property = Property(name, coordinates)
            self.map.add_property(property)
            self.map.save_map()
            ExportadorGeoJSON.export([property], f"{name.replace(' ', '_').lower()}.geojson")

            area = property.area_m2
            perimetro = property.perimeter_m
            messagebox.showinfo("Predio creado", f"Área: {area:,.2f} m²\nPerímetro: {perimetro:,.2f} m\nMapa generado como 'mapa_predios.html'.")
            self.reset_form()
        except Exception as e:
            messagebox.showerror("Error inesperado", str(e))

    def reset_form(self):
        self.name_entry.delete(0, 'end')
        for x_entry, y_entry in self.rows:
            x_entry.destroy()
            y_entry.destroy()
        for label in self.coord_frame.grid_slaves():
            label.destroy()
        self.rows.clear()
        self._crete_headers()
        self.add_row()
