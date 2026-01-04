import ttkbootstrap as tb

from src.ui.create_property_rumbo import CreatePropertyWithRumbos
from src.ui.create_property import CreateProperty
from src.ui.load_real_estates import LoadRealEstates


class HunabKu:
    def __init__(self, root, title=None):
        # Frame principal
        self.main_frame = tb.Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        self.root = root
        if title is None:
            self.root.title("Planos Catastrales")

        self.root.title(title)

        #centrando ventana
        self.root.update()

        # Menú
        self.setup_menu()

        # Footer
        self.setup_footer()

    def setup_menu(self):
        menu_principal = tb.Menu(self.root)
        archivo_menu = tb.Menu(menu_principal, tearoff=0)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir", command=self.root.quit)

        menu_principal.add_cascade(label="Archivo", menu=archivo_menu)
        menu_principal.add_command(label="Carga Masiva", command=self.show_property)
        menu_principal.add_command(label="Geolocalizar", command=self.show_geolocate)
        menu_principal.add_command(label="Predio Coordenadas", command=self.show_geolocate_rumbo)

        self.root.config(menu=menu_principal)

    def setup_footer(self):
        footer_frame = tb.Frame(self.root)
        footer_frame.pack(side="bottom", fill="x")
        copyright_label = tb.Label(
            footer_frame,
            text="© 2025 @crowslayer - Versión 1.0.0",
            font=("Arial", 9),
            foreground="gray"
        )
        copyright_label.pack(pady=5)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_property(self):
        self.clear_main_frame()
        download_frame = LoadRealEstates(self.main_frame)
        download_frame.pack(fill="both", expand=True)

    def show_geolocate(self):
        self.clear_main_frame()
        geolocate_frame = CreateProperty(self.main_frame)
        geolocate_frame.pack(fill="both", expand=True)

    def show_geolocate_rumbo(self):
        self.clear_main_frame()
        geolocate_frame = CreatePropertyWithRumbos(self.main_frame)
        geolocate_frame.pack(fill="both", expand=True)

    def run(self):
        self.root.mainloop()