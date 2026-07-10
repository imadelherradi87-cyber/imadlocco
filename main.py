"""
Kocina del Mundo
Una app de recetas de cocina en español.
Los visitantes pueden ver las recetas libremente.
Solo el administrador puede iniciar sesión para publicar nuevas recetas.
"""

import json
import os

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "cambia_esta_clave"

# ---------- Paleta de colores (cálida, estilo cocina) ----------
COLOR_BG = (0.98, 0.95, 0.89, 1)        # crema
COLOR_PRIMARY = (0.80, 0.33, 0.13, 1)   # terracota
COLOR_PRIMARY_DARK = (0.58, 0.21, 0.08, 1)
COLOR_ACCENT = (0.35, 0.52, 0.29, 1)    # verde oliva
COLOR_DANGER = (0.72, 0.20, 0.18, 1)
COLOR_TEXT = (0.20, 0.13, 0.09, 1)
COLOR_CARD = (1, 1, 1, 1)
COLOR_WHITE = (1, 1, 1, 1)

Window.clearcolor = COLOR_BG


def flat_button(text, bg_color, text_color=COLOR_WHITE, height=dp(50), font_size="16sp", bold=True):
    btn = Button(
        text=text,
        size_hint_y=None,
        height=height,
        background_normal="",
        background_down="",
        background_color=bg_color,
        color=text_color,
        font_size=font_size,
        bold=bold,
    )
    return btn


def autosize_label(text, markup=False, font_size="15sp", color=COLOR_TEXT, bold=False, width_padding=dp(24)):
    lbl = Label(
        text=text,
        markup=markup,
        font_size=font_size,
        color=color,
        bold=bold,
        size_hint_y=None,
        halign="left",
        valign="top",
    )
    lbl.text_size = (Window.width - width_padding, None)
    lbl.bind(texture_size=lambda instance, value: setattr(instance, "height", value[1]))
    return lbl


class RecipeCard(BoxLayout):
    """Tarjeta blanca con esquinas redondeadas usada como fondo de un botón."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*COLOR_CARD)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


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

        # ---- Encabezado ----
        header = BoxLayout(
            size_hint_y=None, height=dp(64), padding=dp(14), spacing=dp(10)
        )
        with header.canvas.before:
            Color(*COLOR_PRIMARY)
            self._header_rect = RoundedRectangle(pos=header.pos, size=header.size, radius=[0])
        header.bind(pos=lambda i, v: setattr(self._header_rect, "pos", v))
        header.bind(size=lambda i, v: setattr(self._header_rect, "size", v))

        title = Label(
            text="🍲 Kocina del Mundo",
            font_size="21sp",
            bold=True,
            color=COLOR_WHITE,
            halign="left",
            valign="middle",
        )
        title.bind(size=title.setter("text_size"))

        admin_btn = flat_button("Admin", COLOR_PRIMARY_DARK, height=dp(40), font_size="14sp")
        admin_btn.size_hint_x = None
        admin_btn.width = dp(90)
        admin_btn.bind(on_press=self.go_to_login)

        header.add_widget(title)
        header.add_widget(admin_btn)
        root.add_widget(header)

        # ---- Lista de recetas ----
        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint_y=None, spacing=dp(10), padding=dp(14))
        grid.bind(minimum_height=grid.setter("height"))

        recipes = load_recipes()
        self.manager_data = recipes

        if not recipes:
            grid.add_widget(Label(
                text="Todavía no hay recetas.",
                color=COLOR_TEXT,
                size_hint_y=None,
                height=dp(40),
            ))

        for index, recipe in enumerate(recipes):
            card = RecipeCard(size_hint_y=None, height=dp(64), padding=dp(2))
            btn = Button(
                text=recipe.get("titulo", "Sin título"),
                background_normal="",
                background_down="",
                background_color=(0, 0, 0, 0),
                color=COLOR_TEXT,
                font_size="17sp",
                bold=True,
                halign="left",
                valign="middle",
            )
            btn.bind(size=lambda i, v: setattr(i, "text_size", v))
            btn.recipe_index = index
            btn.bind(on_press=self.open_recipe)
            card.add_widget(btn)
            grid.add_widget(card)

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
        root = BoxLayout(orientation="vertical")

        # ---- Encabezado con botón volver ----
        header = BoxLayout(size_hint_y=None, height=dp(56), padding=dp(10))
        with header.canvas.before:
            Color(*COLOR_PRIMARY)
            self._header_rect = RoundedRectangle(pos=header.pos, size=header.size, radius=[0])
        header.bind(pos=lambda i, v: setattr(self._header_rect, "pos", v))
        header.bind(size=lambda i, v: setattr(self._header_rect, "size", v))

        back_btn = flat_button("< Volver", COLOR_PRIMARY_DARK, height=dp(40), font_size="14sp")
        back_btn.size_hint_x = None
        back_btn.width = dp(100)
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        header.add_widget(Label())  # spacer
        root.add_widget(header)

        # ---- Contenido con scroll ----
        scroll = ScrollView()
        content = BoxLayout(
            orientation="vertical", size_hint_y=None, spacing=dp(16), padding=dp(18)
        )
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(autosize_label(
            recipe.get("titulo", ""), font_size="23sp", bold=True, color=COLOR_PRIMARY_DARK
        ))

        content.add_widget(autosize_label(
            "[b]🧂 Ingredientes[/b]\n" + recipe.get("ingredientes", ""),
            markup=True, font_size="16sp",
        ))

        content.add_widget(autosize_label(
            "[b]👩‍🍳 Preparación[/b]\n" + recipe.get("pasos", ""),
            markup=True, font_size="16sp",
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
        root = BoxLayout(orientation="vertical", padding=dp(28), spacing=dp(16))

        root.add_widget(Label(
            text="🔐 Acceso de administrador",
            font_size="21sp", bold=True, color=COLOR_PRIMARY_DARK,
            size_hint_y=None, height=dp(44),
        ))

        self.username_input = TextInput(
            hint_text="Usuario", multiline=False, size_hint_y=None, height=dp(50),
            background_color=COLOR_CARD, foreground_color=COLOR_TEXT, padding=[dp(12), dp(14)],
        )
        self.password_input = TextInput(
            hint_text="Contraseña", password=True, multiline=False,
            size_hint_y=None, height=dp(50),
            background_color=COLOR_CARD, foreground_color=COLOR_TEXT, padding=[dp(12), dp(14)],
        )

        root.add_widget(self.username_input)
        root.add_widget(self.password_input)

        login_btn = flat_button("Iniciar sesión", COLOR_ACCENT, height=dp(52))
        login_btn.bind(on_press=self.try_login)
        root.add_widget(login_btn)

        cancel_btn = flat_button("Cancelar", COLOR_DANGER, height=dp(46))
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
        scroll = ScrollView()
        root = BoxLayout(
            orientation="vertical", padding=dp(20), spacing=dp(12), size_hint_y=None
        )
        root.bind(minimum_height=root.setter("height"))

        root.add_widget(Label(
            text="📝 Nueva receta", font_size="21sp", bold=True, color=COLOR_PRIMARY_DARK,
            size_hint_y=None, height=dp(44),
        ))

        self.title_input = TextInput(
            hint_text="Título", multiline=False, size_hint_y=None, height=dp(50),
            background_color=COLOR_CARD, foreground_color=COLOR_TEXT, padding=[dp(12), dp(14)],
        )
        self.ingredients_input = TextInput(
            hint_text="Ingredientes", multiline=True, size_hint_y=None, height=dp(120),
            background_color=COLOR_CARD, foreground_color=COLOR_TEXT, padding=[dp(12), dp(10)],
        )
        self.steps_input = TextInput(
            hint_text="Preparación", multiline=True, size_hint_y=None, height=dp(160),
            background_color=COLOR_CARD, foreground_color=COLOR_TEXT, padding=[dp(12), dp(10)],
        )

        root.add_widget(self.title_input)
        root.add_widget(self.ingredients_input)
        root.add_widget(self.steps_input)

        save_btn = flat_button("Guardar receta", COLOR_ACCENT, height=dp(52))
        save_btn.bind(on_press=self.save_recipe)
        root.add_widget(save_btn)

        back_btn = flat_button("Volver al panel", COLOR_PRIMARY_DARK, height=dp(46))
        back_btn.bind(on_press=self.go_back)
        root.add_widget(back_btn)

        scroll.add_widget(root)
        self.add_widget(scroll)

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