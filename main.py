"""
Kocina del Mundo
Una app de recetas de cocina en español.
Los visitantes pueden ver las recetas libremente.
Solo el administrador puede iniciar sesión para publicar nuevas recetas.
"""

import json
import os

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.metrics import dp

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "cambia_esta_clave"


def get_data_path():
    app = App.get_running_app()
    if app:
        return os.path.join(app.user_data_dir, "recetas.json")
    return "recetas.json"


def load_recipes():
    path = get_data_path()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return [
        {
            "titulo": "Tortilla Española",
            "ingredientes": "6 huevos, 4 patatas, 1 cebolla, aceite de oliva, sal",
            "pasos": "1. Pela y corta las patatas y la cebolla.\n"
                      "2. Fríelas en aceite hasta que estén blandas.\n"
                      "3. Bate los huevos y mezcla con las patatas.\n"
                      "4. Cuaja la mezcla en la sartén por ambos lados.",
        }
    ]


def save_recipes(recipes):
    path = get_data_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(recipes, f, ensure_ascii=False, indent=2)


class RecipeListScreen(Screen):
    def on_pre_enter(self, *args):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")

        header = BoxLayout(size_hint_y=None, height=dp(60), padding=dp(8))
        title = Label(text="Kocina del Mundo", font_size="22sp", bold=True)
        admin_btn = Button(text="Admin", size_hint_x=None, width=dp(90))
        admin_btn.bind(on_press=self.go_to_login)
        header.add_widget(title)
        header.add_widget(admin_btn)
        root.add_widget(header)

        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint_y=None, spacing=dp(6), padding=dp(8))
        grid.bind(minimum_height=grid.setter("height"))

        recipes = load_recipes()
        self.manager_data = recipes

        if not recipes:
            grid.add_widget(Label(text="Todavía no hay recetas.", size_hint_y=None, height=dp(40)))

        for index, recipe in enumerate(recipes):
            btn = Button(
                text=recipe.get("titulo", "Sin título"),
                size_hint_y=None,
                height=dp(50),
            )
            btn.recipe_index = index
            btn.bind(on_press=self.open_recipe)
            grid.add_widget(btn)

        scroll.add_widget(grid)
        root.add_widget(scroll)

        self.add_widget(root)

    def open_recipe(self, instance):
        detail_screen = self.manager.get_screen("detail")
        detail_screen.load_recipe(instance.recipe_index)
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "detail"

    def go_to_login(self, instance):
        self.manager.transition = SlideTransition(direction="up")
        self.manager.current = "login"


class RecipeDetailScreen(Screen):
    def load_recipe(self, index):
        self.recipe_index = index
        recipes = load_recipes()
        recipe = recipes[index]

        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))

        back_btn = Button(text="< Volver", size_hint_y=None, height=dp(45))
        back_btn.bind(on_press=self.go_back)
        root.add_widget(back_btn)

        title = Label(
            text=recipe.get("titulo", ""),
            font_size="20sp",
            bold=True,
            size_hint_y=None,
            height=dp(40),
        )
        root.add_widget(title)

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(10), padding=dp(4))
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(Label(
            text="[b]Ingredientes:[/b]\n" + recipe.get("ingredientes", ""),
            markup=True,
            size_hint_y=None,
            text_size=(self.width - dp(24), None),
            halign="left",
        ))
        content.add_widget(Label(
            text="[b]Preparación:[/b]\n" + recipe.get("pasos", ""),
            markup=True,
            size_hint_y=None,
            text_size=(self.width - dp(24), None),
            halign="left",
        ))

        scroll.add_widget(content)
        root.add_widget(scroll)

        self.add_widget(root)

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "list"


class LoginScreen(Screen):
    def on_pre_enter(self, *args):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=dp(24), spacing=dp(14))

        root.add_widget(Label(text="Acceso de administrador", font_size="20sp", bold=True,
                               size_hint_y=None, height=dp(40)))

        self.username_input = TextInput(hint_text="Usuario", multiline=False, size_hint_y=None, height=dp(48))
        self.password_input = TextInput(hint_text="Contraseña", password=True, multiline=False,
                                         size_hint_y=None, height=dp(48))

        root.add_widget(self.username_input)
        root.add_widget(self.password_input)

        login_btn = Button(text="Iniciar sesión", size_hint_y=None, height=dp(50))
        login_btn.bind(on_press=self.try_login)
        root.add_widget(login_btn)

        cancel_btn = Button(text="Cancelar", size_hint_y=None, height=dp(45))
        cancel_btn.bind(on_press=self.cancel)
        root.add_widget(cancel_btn)

        root.add_widget(Label())

        self.add_widget(root)

    def try_login(self, instance):
        user = self.username_input.text.strip()
        pwd = self.password_input.text

        if user == ADMIN_USERNAME and pwd == ADMIN_PASSWORD:
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = "add_recipe"
        else:
            popup = Popup(
                title="Error",
                content=Label(text="Usuario o contraseña incorrectos."),
                size_hint=(0.8, 0.3),
            )
            popup.open()

    def cancel(self, instance):
        self.manager.transition = SlideTransition(direction="down")
        self.manager.current = "list"


class AddRecipeScreen(Screen):
    def on_pre_enter(self, *args):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))

        root.add_widget(Label(text="Nueva receta", font_size="20sp", bold=True,
                               size_hint_y=None, height=dp(40)))

        self.title_input = TextInput(hint_text="Título", multiline=False,
                                      size_hint_y=None, height=dp(48))
        self.ingredients_input = TextInput(hint_text="Ingredientes", multiline=True,
                                            size_hint_y=None, height=dp(120))
        self.steps_input = TextInput(hint_text="Preparación", multiline=True,
                                      size_hint_y=None, height=dp(160))

        root.add_widget(self.title_input)
        root.add_widget(self.ingredients_input)
        root.add_widget(self.steps_input)

        save_btn = Button(text="Guardar receta", size_hint_y=None, height=dp(50))
        save_btn.bind(on_press=self.save_recipe)
        root.add_widget(save_btn)

        back_btn = Button(text="Volver al panel", size_hint_y=None, height=dp(45))
        back_btn.bind(on_press=self.go_back)
        root.add_widget(back_btn)

        self.add_widget(root)

    def save_recipe(self, instance):
        title = self.title_input.text.strip()
        if not title:
            popup = Popup(
                title="Falta información",
                content=Label(text="Por favor, añade un título."),
                size_hint=(0.8, 0.3),
            )
            popup.open()
            return

        recipes = load_recipes()
        recipes.append({
            "titulo": title,
            "ingredientes": self.ingredients_input.text.strip(),
            "pasos": self.steps_input.text.strip(),
        })
        save_recipes(recipes)

        self.title_input.text = ""
        self.ingredients_input.text = ""
        self.steps_input.text = ""

        popup = Popup(
            title="Guardado",
            content=Label(text="¡Receta publicada con éxito!"),
            size_hint=(0.8, 0.3),
        )
        popup.open()

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "list"


class KocinaApp(App):
    def build(self):
        self.title = "Kocina del Mundo"
        sm = ScreenManager()
        sm.add_widget(RecipeListScreen(name="list"))
        sm.add_widget(RecipeDetailScreen(name="detail"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(AddRecipeScreen(name="add_recipe"))
        sm.current = "list"
        return sm


if __name__ == "__main__":
    KocinaApp().run()