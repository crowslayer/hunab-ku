import logging
import ttkbootstrap as tb
import os
import sys
from typing import Optional
from ui.HunabKu import HunabKu


def resource_path(relative_path: str) -> str:
    base_path: Optional[str]
    if hasattr(sys, '_MEIPASS'):
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    else:
        base_path = os.path.dirname(__file__) #os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def run():
    logging.basicConfig(level=logging.INFO)
    app_width, app_height = 900, 600
    root = tb.Window(themename="cosmo", size=(app_width, app_height))
    # Centrar la ventana
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = int((screen_width / 2) - (app_width / 2))
    y = int((screen_height / 2) - (app_height / 2))

    #Agregando icono
    # Cargar icono con manejo de errores
    try:
        icon_path = resource_path("main.ico")
        #icon_path = os.path.join(os.path.dirname(__file__), "main.ico")

        root.iconbitmap(icon_path)
    except Exception as e:
        logging.warning(f"No se pudo cargar el icono: {e}")

    root.geometry(f'{app_width}x{app_height}+{x}+{y}')

    app = HunabKu(root, "Hunab Ku")
    app.run()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run()

