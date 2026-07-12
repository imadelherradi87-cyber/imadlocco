"""
Kocina del Mundo
Una app de recetas de cocina en español.
"""

import json
import os
import base64
import io

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.core.image import Image as CoreImage
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle, Rectangle

from constants import (
    ADMIN_USERNAME, ADMIN_PASSWORD, CATEGORIES,
    COLOR_BG, COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_ACCENT,
    COLOR_DANGER, COLOR_TEXT, COLOR_CARD, COLOR_WHITE,
)

Window.clearcolor = COLOR_BG
Window.clearcolor = COLOR_BG

# ---------- Logo (cargado desde logo_data.py en base64) ----------
def _load_logo_texture():
    try:
        from logo_data import HEADER_LOGO_BASE64
        raw = base64.b64decode(HEADER_LOGO_BASE64)
        buf = io.BytesIO(raw)
        core_img = CoreImage(buf, ext="png")
        return core_img.texture
    except Exception:
        return None


_LOGO_TEXTURE = _load_logo_texture()
LOGO_HEIGHT = dp(44)
LOGO_WIDTH = dp(66)
if _LOGO_TEXTURE:
    ratio = _LOGO_TEXTURE.width / _LOGO_TEXTURE.height
    LOGO_WIDTH = LOGO_HEIGHT * ratio


class LogoImage(Widget):
    def __init__(self, texture, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(texture=texture, pos=self.pos, size=self.size)
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


def flat_button(text, bg_color, text_color=COLOR_WHITE, height=dp(50), font_size="16sp", bold=True):
    return Button(
        text=text, size_hint_y=None, height=height,
        background_normal="", background_down="",
        background_color=bg_color, color=text_color,
        font_size=font_size, bold=bold,
    )


def autosize_label(text, markup=False, font_size="15sp", color=COLOR_TEXT, bold=False, width_padding=dp(24)):
    lbl = Label(
        text=text, markup=markup, font_size=font_size, color=color, bold=bold,
        size_hint_y=None, halign="left", valign="top",
    )
    lbl.text_size = (Window.width - width_padding, None)
    lbl.bind(texture_size=lambda instance, value: setattr(instance, "height", value[1]))
    return lbl


class RecipeCard(BoxLayout):
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
            "categoria": "Cocina Española",
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


def make_header():
    header = BoxLayout(size_hint_y=None, height=dp(64), padding=dp(10), spacing=dp(8))
    with header.canvas.before:
        Color(*COLOR_PRIMARY)
        rect = RoundedRectangle(pos=header.pos, size=header.size, radius=[0])
    header.bind(pos=lambda i, v: setattr(rect, "pos", v))
    header.bind(size=lambda i, v: setattr(rect, "size", v))

    if _LOGO_TEXTURE:
        logo = LogoImage(texture=_LOGO_TEXTURE, size_hint=(None, None),
                          width=LOGO_WIDTH, height=LOGO_HEIGHT)
    else:
        logo = Label(text="Kocina del Mundo", font_size="20sp", bold=True, color=COLOR_WHITE)

    header.add_widget(logo)
    return header


class RecipeListScreen(Screen):
    def on_pre_enter(self, *args):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        header = make_header()

        cat_btn = flat_button("☰ Categorías", COLOR_PRIMARY_DARK, height=dp(40), font_size="13sp")
        cat_btn.size_hint_x = None
        cat_btn.width = dp(110)
        cat_btn.bind(on_press=self.go_to_categories)

        admin_btn = flat_button("Admin", COLOR_PRIMARY_DARK, height=dp(40), font_size="14sp")
        admin_btn.size_hint_x = None
        admin_btn.width = dp(80)
        admin_btn.bind(on_press=self.go_to_login)

        header.add_widget(Label())
        header.add_widget(cat_btn)
        header.add_widget(admin_btn)
        root.add_widget(header)

        app = App.get_running_app()
        active_filter = getattr(app, "selected_category", None)

        if active_filter:
            filter_bar = BoxLayout(size_hint_y=None, height=dp(40), padding=(dp(14), dp(4)), spacing=dp(8))
            filter_bar.add_widget(Label(
                text=f"Filtrando: {active_filter}", color=COLOR_TEXT, font_size="13sp",
            ))
            clear_btn = flat_button("✕ Quitar filtro", COLOR_DANGER, height=dp(32), font_size="12sp")
            clear_btn.size_hint_x = None
            clear_btn.width = dp(130)
            clear_btn.bind(on_press=self.clear_filter)
            filter_bar.add_widget(clear_btn)
            root.add_widget(filter_bar)

        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint_y=None, spacing=dp(10), padding=dp(14))
        grid.bind(minimum_height=grid.setter("height"))

        recipes = load_recipes()
        if active_filter:
            recipes = [r for r in recipes if r.get("categoria") == active_filter]
        self.manager_data = recipes

        if not recipes:
            grid.add_widget(Label(
                text="No hay recetas en esta categoría todavía.",
                color=COLOR_TEXT, size_hint_y=None, height=dp(40),
            ))

        for index, recipe in enumerate(recipes):
            card = RecipeCard(size_hint_y=None, height=dp(64), padding=dp(2))
            btn = Button(
                text=recipe.get("titulo", "Sin título"),
                background_normal="", background_down="", background_color=(0, 0, 0, 0),
                color=COLOR_TEXT, font_size="17sp", bold=True, halign="left", valign="middle",
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
        detail_screen.load_recipe(instance.recipe_index, self.manager_data)
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "detail"

    def go_to_login(self, instance):
        self.manager.transition = SlideTransition(direction="up")
        self.manager.current = "login"

    def go_to_categories(self, instance):
        self.manager.transition = SlideTransition(direction="down")
        self.manager.current = "categories"

    def clear_filter(self, instance):
        App.get_running_app().selected_category = None
        self.build_ui()


class CategoriesScreen(Screen):
    def on_pre_enter(self, *args):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        header = make_header()
        back_btn = flat_button("< Volver", COLOR_PRIMARY_DARK, height=dp(40), font_size="13sp")
        back_btn.size_hint_x = None
        back_btn.width = dp(100)
        back_btn.bind(on_press=self.go_back)
        header.add_widget(Label())
        header.add_widget(back_btn)
        root.add_widget(header)

        scroll = ScrollView()
        grid = GridLayout(cols=1, size_hint_y=None, spacing=dp(10), padding=dp(14))
        grid.bind(minimum_height=grid.setter("height"))

        grid.add_widget(Label(
            text="📋 Categorías", font_size="20sp", bold=True, color=COLOR_PRIMARY_DARK,
            size_hint_y=None, height=dp(40),
        ))

        for cat in CATEGORIES:
            card = RecipeCard(size_hint_y=None, height=dp(56), padding=dp(2))
            btn = Button(
                text=cat, background_normal="", background_down="", background_color=(0, 0, 0, 0),
                color=COLOR_TEXT, font_size="16sp", bold=True, halign="left", valign="middle",
            )
            btn.bind(size=lambda i, v: setattr(i, "text_size", v))
            btn.category_name = cat
            btn.bind(on_press=self.select_category)
            card.add_widget(btn)
            grid.add_widget(card)

        scroll.add_widget(grid)
        root.add_widget(scroll)
        self.add_widget(root)

    def select_category(self, instance):
        App.get_running_app().selected_category = instance.category_name
        self.manager.transition = SlideTransition(direction="up")
        self.manager.current = "list"

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "list"


class RecipeDetailScreen(Screen):
    def load_recipe(self, index, recipe_list=None):
        recipes = recipe_list if recipe_list is not None else load_recipes()
        recipe = recipes[index]

        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        header = BoxLayout(size_hint_y=None, height=dp(56), padding=dp(10))
        with header.canvas.before:
            Color(*COLOR_PRIMARY)
            rect = RoundedRectangle(pos=header.pos, size=header.size, radius=[0])
        header.bind(pos=lambda i, v: setattr(rect, "pos", v))
        header.bind(size=lambda i, v: setattr(rect, "size", v))

        back_btn = flat_button("< Volver", COLOR_PRIMARY_DARK, height=dp(40), font_size="14sp")
        back_btn.size_hint_x = None
        back_btn.width = dp(100)
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)
        header.add_widget(Label())
        root.add_widget(header)

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(16), padding=dp(18))
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(autosize_label(
            recipe.get("titulo", ""), font_size="23sp", bold=True, color=COLOR_PRIMARY_DARK
        ))
        if recipe.get("categoria"):
            content.add_widget(autosize_label(
                "🏷️ " + recipe.get("categoria"), font_size="14sp", color=COLOR_ACCENT, bold=True
            ))
        content.add_widget(autosize_label(
            "[b]🧂 Ingredientes[/b]\n" + recipe.get("ingredientes", ""), markup=True, font_size="16sp",
        ))
        content.add_widget(autosize_label(
            "[b]👩‍🍳 Preparación[/b]\n" + recipe.get("pasos", ""), markup=True, font_size="16sp",
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
            text="🔐 Acceso de administrador", font_size="21sp", bold=True, color=COLOR_PRIMARY_DARK,
            size_hint_y=None, height=dp(44),
        ))

        self.username_input = TextInput(
            hint_text="Usuario", multiline=False, size_hint_y=None, height=dp(50),
            background_color=COLOR_CARD, foreground_color=COLOR_TEXT, padding=[dp(12), dp(14)],
        )
        self.password_input = TextInput(
            hint_text="Contraseña", password=True, multiline=False, size_hint_y=None, height=dp(50),
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
            Popup(title="Error", content=Label(text="Usuario o contraseña incorrectos."),
                  size_hint=(0.8, 0.3)).open()

    def cancel(self, instance):
        self.manager.transition = SlideTransition(direction="down")
        self.manager.current = "list"


class AddRecipeScreen(Screen):
    def on_pre_enter(self, *args):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        scroll = ScrollView()
        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(12), size_hint_y=None)
        root.bind(minimum_height=root.setter("height"))

        root.add_widget(Label(
            text="📝 Nueva receta", font_size="21sp", bold=True, color=COLOR_PRIMARY_DARK,
            size_hint_y=None, height=dp(44),
        ))

        self.title_input = TextInput(
            hint_text="Título", multiline=False, size_hint_y=None, height=dp(50),
            background_color=COLOR_CARD, foreground_color=COLOR_TEXT, padding=[dp(12), dp(14)],
        )
        self.category_spinner = Spinner(
            text=CATEGORIES[0], values=CATEGORIES, size_hint_y=None, height=dp(50),
            background_color=COLOR_CARD, color=COLOR_TEXT,
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
        root.add_widget(Label(text="Categoría:", size_hint_y=None, height=dp(24), color=COLOR_TEXT))
        root.add_widget(self.category_spinner)
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
            Popup(title="Falta información", content=Label(text="Por favor, añade un título."),
                  size_hint=(0.8, 0.3)).open()
            return

        recipes = load_recipes()
        recipes.append({
            "titulo": title,
            "categoria": self.category_spinner.text,
            "ingredientes": self.ingredients_input.text.strip(),
            "pasos": self.steps_input.text.strip(),
        })
        save_recipes(recipes)

        self.title_input.text = ""
        self.ingredients_input.text = ""
        self.steps_input.text = ""

        Popup(title="Guardado", content=Label(text="¡Receta publicada con éxito!"),
              size_hint=(0.8, 0.3)).open()

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "list"


class KocinaApp(App):
    selected_category = None

    def build(self):
        self.title = "Kocina del Mundo"
        sm = ScreenManager()
        sm.add_widget(RecipeListScreen(name="list"))
        sm.add_widget(CategoriesScreen(name="categories"))
        sm.add_widget(RecipeDetailScreen(name="detail"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(AddRecipeScreen(name="add_recipe"))
        sm.current = "list"
        return sm


if __name__ == "__main__":
    KocinaApp().run()
