import ttkbootstrap as tb
from tkinter import messagebox

from models.plano import PlanoCatastral
from models.mapa import Mapa


class CreatePropertyWithRumbos(tb.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.rows = []
        self.mapa = Mapa()

        # Título
        tb.Label(self, text="Ingreso por rumbo y distancia",
                 font=("Segoe UI", 12, "bold")).pack(pady=(10, 5))

        # Campo: nombre del predio
        name_frame = tb.Frame(self)
        name_frame.pack(pady=5)
        tb.Label(name_frame, text="Nombre del predio:").pack(side="left")
        self.name_entry = tb.Entry(name_frame, width=30)
        self.name_entry.pack(side="left", padx=10)

        # Tipo de coordenada
        type_frame = tb.Frame(self)
        type_frame.pack(pady=(5, 0))
        tb.Label(type_frame, text="Tipo de coordenada:").pack(side="left")

        self.type_var = tb.StringVar(value="UTM")
        self.type_combo = tb.Combobox(type_frame, textvariable=self.type_var,
                                      values=["UTM", "Decimal", "DMS"],
                                      state="readonly", width=15)
        self.type_combo.pack(side="left", padx=10)
        self.type_combo.bind("<<ComboboxSelected>>", self._actualizar_estado_combo)

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
                                       state="readonly", width=40)
        self.state_combo.pack(side="left", padx=10)

        # Punto inicial
        initial_frame = tb.Frame(self)
        initial_frame.pack(pady=5)
        tb.Label(initial_frame, text="Latitud inicial:").pack(side="left")
        self.lat_entry = tb.Entry(initial_frame, width=20)
        self.lat_entry.pack(side="left", padx=5)

        tb.Label(initial_frame, text="Longitud inicial:").pack(side="left")
        self.lon_entry = tb.Entry(initial_frame, width=20)
        self.lon_entry.pack(side="left", padx=5)

        # Contenedor de rumbos
        self.rumbo_frame = tb.Frame(self)
        self.rumbo_frame.pack(pady=10)

        self._crete_headers()

        self.add_row()

        # Botones
        btn_frame = tb.Frame(self)
        btn_frame.pack(pady=10)

        tb.Button(btn_frame, text="Agregar segmento", command=self.add_row).pack(side="left", padx=10)
        tb.Button(btn_frame, text="Crear predio y mostrar mapa", command=self.create_property).pack(side="left", padx=10)

    def _crete_headers(self):
        headers = ["#", "Rumbo (ej. N 45°30'0'' E)", "Distancia (m)"]
        for i, h in enumerate(headers):
            tb.Label(self.rumbo_frame, text=h).grid(row=0, column=i, padx=5, pady=5)


    def _actualizar_estado_combo(self, event=None):
        if self.type_var.get() == "UTM":
            self.state_combo.configure(state="readonly")
        else:
            self.state_combo.set("")
            self.state_combo.configure(state="disabled")

    def _zona_desde_estado(self):
        estado = self.state_var.get()
        if "Zona 11" in estado:
            return 11
        elif "Zona 12" in estado:
            return 12
        elif "Zona 13" in estado:
            return 13
        elif "Zona 14" in estado:
            return 14
        elif "Zona 15" in estado:
            return 15
        elif "Zona 16" in estado:
            return 16
        elif "Zona 17" in estado:
            return 17
        return 16  # default


    def add_row(self):
        row_idx = len(self.rows) + 1
        rumbo_entry = tb.Entry(self.rumbo_frame, width=20)
        dist_entry = tb.Entry(self.rumbo_frame, width=10)

        tb.Label(self.rumbo_frame, text=row_idx).grid(row=row_idx, column=0, padx=5, pady=2)
        rumbo_entry.grid(row=row_idx, column=1, padx=5, pady=2)
        dist_entry.grid(row=row_idx, column=2, padx=5, pady=2)

        self.rows.append((rumbo_entry, dist_entry))

    def create_property(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Debe ingresar un nombre para el predio.")
            return

        try:
            lat0 = float(self.lat_entry.get().replace(",", ""))
            lon0 = float(self.lon_entry.get().replace(",", ""))
        except ValueError:
            messagebox.showerror("Error", "Latitud y longitud inicial deben ser válidos.")
            return

        zona = self._zona_desde_estado() if self.type_var.get() == "UTM" else 16
        plano = PlanoCatastral(lat0, lon0)

        for rumbo_entry, dist_entry in self.rows:
            rumbo = rumbo_entry.get().strip()
            try:
                distancia = float(dist_entry.get().replace(",", ""))
            except ValueError:
                messagebox.showerror("Error", "Verifica que todas las distancias sean numéricas.")
                return

            if not rumbo:
                messagebox.showerror("Error", "Todos los campos de rumbo deben estar completos.")
                return

            try:
                plano.add_segment(rumbo, distancia)
            except ValueError as e:
                messagebox.showerror("Error en rumbo", str(e))
                return

        try:
            property = plano.add_property(name)
            self.mapa.add_property(property)
            self.mapa.save_map()

            area = property.area_m2
            perimeter = property.perimeter_m
            messagebox.showinfo("Predio creado", f"Área: {area:,.2f} m²\nPerímetro: {perimeter:,.2f} m\nMapa generado como 'mapa_predios.html'.")

        except Exception as e:
            messagebox.showerror("Error inesperado", str(e))
