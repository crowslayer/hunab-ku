import webbrowser
import os

class RenderInBrowser:

    @staticmethod
    def show_map(map_name):
        path_filename = os.path.abspath(f"{map_name}.html")
        webbrowser.open_new_tab(f"file://{path_filename}")

    @staticmethod
    def show(filename):
        path_filename = os.path.abspath(filename)
        webbrowser.open_new_tab(f"file://{path_filename}")

    @staticmethod
    def show_json(filename):
        path_filename = os.path.abspath(filename)
        webbrowser.open_new_tab(f"file://{path_filename}.json")