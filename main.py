"""
Kocina del Mundo
App nativa que refleja la estructura real del sitio
https://kocinadelmundo24.blogspot.com (recetas cargadas en vivo desde Blogger).
"""

import webbrowser

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, RoundedRectangle

from constants import (
    CATEGORIES, BLOG_URL,
    COLOR_BG, COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_ACCENT,
    COLOR_DANGER, COLOR_TEXT, COLOR_CARD, COLOR_WHITE,
)

Window.clearcolor = COLOR_BG

from logo import LOGO_TEXTURE, LOGO_HEIGHT, LOGO_WIDTH, LogoImage
from blogger_api import fetch_posts


# ---------------------------------------------------------------------------
# Helpers de UI (mismo estilo que antes)
# ---------------------------------------------------------------------------

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


def make_header(show_back=False, on_back=None):
    header = BoxLayout(size_hint_y=None, height=dp(64), padding=dp(10), spacing=dp(8))
    with header.canvas.before:
        Color(*COLOR_PRIMARY)
        rect = RoundedRectangle(pos=header.pos, size=header.size, radius=[0])
        header.bind(pos=lambda i, v: setattr(rect, "pos", v))
        header.bind(size=lambda i, v: setattr(rect, "size", v))

    if show_back:
        back_btn = flat_button("< Volver", COLOR_PRIMARY_DARK, height=dp(40), font_size="13sp")
        back_btn.size_hint_x = None
        back_btn.width = dp(90)
        if on_back:
            back_btn.bind(on_press=on_back)
        header.add_widget(back_btn)

    if LOGO_TEXTURE:
        logo = LogoImage(texture=LOGO_TEXTURE, size_hint=(None, None),
                          width=LOGO_WIDTH, height=LOGO_HEIGHT)
    else:
        logo = Label(text="Kocina del Mundo", font_size="18sp", bold=True, color=COLOR_WHITE)
    header.add_widget(logo)
    return header


def make_recipe_card(post, on_press):
    """Tarjeta de receta con miniatura, título y fecha (igual que la web)."""
    card = RecipeCard(orientation="horizontal", size_hint_y=None, height=dp(96),
                       padding=dp(8), spacing=dp(10))

    if post.get("imagen"):
        thumb = AsyncImage(source=post["imagen"], size_hint=(None, None),
                            width=dp(80), height=dp(80))
    else:
        thumb = BoxLayout(size_hint=(None, None), width=dp(80), height=dp(80))
    card.add_widget(thumb)

    info = BoxLayout(orientation="vertical", spacing=dp(4))
    title_lbl = autosize_label(post.get("titulo", ""), font_size="16sp", bold=True,
                                color=COLOR_TEXT, width_padding=dp(120))
    info.add_widget(title_lbl)
    if post.get("categorias"):
        cat_lbl = autosize_label(" · ".join(post["categorias"][:3]), font_size="12sp",
                                  color=COLOR_ACCENT, width_padding=dp(120))
        info.add_widget(cat_lbl)
    card.add_widget(info)

    btn = Button(background_normal="", background_down="", background_color=(0, 0, 0, 0))
    btn.bind(on_press=lambda i: on_press(post))
    card.add_widget(btn)
    return card


def loading_label(text="Cargando recetas..."):
    return Label(text=text, color=COLOR_TEXT, size_hint_y=None, height=dp(60), font_size="15sp")


def error_label(text="No se pudieron cargar las recetas. Revisa tu conexión."):
    return Label(text=text, color=COLOR_DANGER, size_hint_y=None, height=dp(60), font_size="14sp")


# ---------------------------------------------------------------------------
# Home: refleja la portada del sitio (destacadas + categorías + rejilla)
# ---------------------------------------------------------------------------

class HomeScreen(Screen):
    def on_pre_enter(self, *args):
        self.build_ui()
        self.load_posts()

    def build_ui(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(make_header())

        # Barra de búsqueda
        search_bar = BoxLayout(size_hint_y=None, height=dp(50), padding=dp(10), spacing=dp(8))
        self.search_input = TextInput(
            hint_text="Buscar recetas...", multiline=False,
            background_color=COLOR_CARD, foreground_color=COLOR_TEXT,
            size_hint_x=1, padding=[dp(10), dp(10)],
        )
        self.search_input.bind(on_text_validate=self.do_search)
        search_btn = flat_button("Buscar", COLOR_ACCENT, height=dp(44), font_size="13sp")
        search_btn.size_hint_x = None
        search_btn.width = dp(90)
        search_btn.bind(on_press=self.do_search)
        search_bar.add_widget(self.search_input)
        search_bar.add_widget(search_btn)
        root.add_widget(search_bar)

        # Categorías principales (igual que el menú de la web)
        cat_scroll = ScrollView(size_hint_y=None, height=dp(56), do_scroll_y=False, do_scroll_x=True)
        cat_row = BoxLayout(size_hint_x=None, spacing=dp(8), padding=(dp(10), dp(6)))
        cat_row.bind(minimum_width=cat_row.setter("width"))
        for cat_name in CATEGORIES.keys():
            btn = flat_button(cat_name, COLOR_PRIMARY_DARK, height=dp(44), font_size="13sp")
            btn.size_hint_x = None
            btn.width = dp(120)
            btn.category_name = cat_name
            btn.bind(on_press=self.open_category)
            cat_row.add_widget(btn)
        cat_scroll.add_widget(cat_row)
        root.add_widget(cat_scroll)

        # Contenedor de resultados (se llena al cargar)
        self.results_scroll = ScrollView()
        self.results_grid = GridLayout(cols=1, size_hint_y=None, spacing=dp(10), padding=dp(14))
        self.results_grid.bind(minimum_height=self.results_grid.setter("height"))
        self.results_grid.add_widget(loading_label())
        self.results_scroll.add_widget(self.results_grid)
        root.add_widget(self.results_scroll)

        self.add_widget(root)

    def load_posts(self, query=None):
        self.results_grid.clear_widgets()
        self.results_grid.add_widget(loading_label())
        fetch_posts(self.show_posts, on_error=self.show_error, query=query, max_results=20)

    def show_posts(self, posts):
        self.results_grid.clear_widgets()
        self.results_grid.add_widget(autosize_label(
            "Últimas recetas" if not posts else f"Últimas recetas ({len(posts)})",
            font_size="17sp", bold=True, color=COLOR_PRIMARY_DARK,
        ))
        if not posts:
            self.results_grid.add_widget(Label(
                text="No se encontraron recetas.", color=COLOR_TEXT,
                size_hint_y=None, height=dp(40),
            ))
        for post in posts:
            self.results_grid.add_widget(make_recipe_card(post, self.open_detail))

    def show_error(self, err):
        self.results_grid.clear_widgets()
        self.results_grid.add_widget(error_label())

    def do_search(self, instance):
        query = self.search_input.text.strip()
        if query:
            self.load_posts(query=query)
        else:
            self.load_posts()

    def open_category(self, instance):
        cat_screen = self.manager.get_screen("category")
        cat_screen.set_category(instance.category_name)
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "category"

    def open_detail(self, post):
        detail_screen = self.manager.get_screen("detail")
        detail_screen.show_post(post, return_to="home")
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "detail"


# ---------------------------------------------------------------------------
# Categoría: muestra subcategorías reales + recetas filtradas
# ---------------------------------------------------------------------------

class CategoryScreen(Screen):
    current_category = None

    def set_category(self, category_name):
        self.current_category = category_name
        self.build_ui()
        self.load_posts(category_name)

    def build_ui(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(make_header(show_back=True, on_back=self.go_back))

        root.add_widget(autosize_label(
            self.current_category or "", font_size="20sp", bold=True,
            color=COLOR_PRIMARY_DARK, width_padding=dp(24),
        ))

        # Subcategorías reales como chips
        subcats = CATEGORIES.get(self.current_category, [])
        chip_scroll = ScrollView(size_hint_y=None, height=dp(50), do_scroll_y=False, do_scroll_x=True)
        chip_row = BoxLayout(size_hint_x=None, spacing=dp(6), padding=(dp(10), dp(4)))
        chip_row.bind(minimum_width=chip_row.setter("width"))

        all_btn = flat_button("Todo", COLOR_ACCENT, height=dp(38), font_size="12sp")
        all_btn.size_hint_x = None
        all_btn.width = dp(80)
        all_btn.bind(on_press=lambda i: self.load_posts(self.current_category))
        chip_row.add_widget(all_btn)

        for sub in subcats:
            chip = flat_button(sub, COLOR_PRIMARY_DARK, height=dp(38), font_size="12sp")
            chip.size_hint_x = None
            chip.width = dp(110)
            chip.sub_name = sub
            chip.bind(on_press=lambda i: self.load_posts(i.sub_name))
            chip_row.add_widget(chip)

        chip_scroll.add_widget(chip_row)
        root.add_widget(chip_scroll)

        self.results_scroll = ScrollView()
        self.results_grid = GridLayout(cols=1, size_hint_y=None, spacing=dp(10), padding=dp(14))
        self.results_grid.bind(minimum_height=self.results_grid.setter("height"))
        self.results_scroll.add_widget(self.results_grid)
        root.add_widget(self.results_scroll)

        self.add_widget(root)

    def load_posts(self, label):
        self.results_grid.clear_widgets()
        self.results_grid.add_widget(loading_label())
        fetch_posts(self.show_posts, on_error=self.show_error, label=label, max_results=20)

    def show_posts(self, posts):
        self.results_grid.clear_widgets()
        if not posts:
            self.results_grid.add_widget(Label(
                text="No hay recetas en esta categoría todavía.",
                color=COLOR_TEXT, size_hint_y=None, height=dp(40),
            ))
        for post in posts:
            self.results_grid.add_widget(make_recipe_card(post, self.open_detail))

    def show_error(self, err):
        self.results_grid.clear_widgets()
        self.results_grid.add_widget(error_label())

    def open_detail(self, post):
        detail_screen = self.manager.get_screen("detail")
        detail_screen.show_post(post, return_to="category")
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "detail"

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "home"


# ---------------------------------------------------------------------------
# Detalle de receta: contenido real del post
# ---------------------------------------------------------------------------

class RecipeDetailScreen(Screen):
    return_to = "home"

    def show_post(self, post, return_to="home"):
        self.current_post = post
        self.return_to = return_to
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(make_header(show_back=True, on_back=self.go_back))

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(14), padding=dp(18))
        content.bind(minimum_height=content.setter("height"))

        if post.get("imagen"):
            content.add_widget(AsyncImage(
                source=post["imagen"], size_hint=(1, None), height=dp(220),
                allow_stretch=True, keep_ratio=True,
            ))

        content.add_widget(autosize_label(
            post.get("titulo", ""), font_size="22sp", bold=True, color=COLOR_PRIMARY_DARK,
        ))

        if post.get("categorias"):
            content.add_widget(autosize_label(
                "🏷️ " + " · ".join(post["categorias"]), font_size="13sp", color=COLOR_ACCENT, bold=True,
            ))

        content.add_widget(autosize_label(
            post.get("contenido_texto", "") or "Contenido no disponible.",
            font_size="15sp",
        ))

        if post.get("link"):
            web_btn = flat_button("Ver receta completa en la web", COLOR_ACCENT, height=dp(48))
            web_btn.bind(on_press=lambda i: webbrowser.open(post["link"]))
            content.add_widget(web_btn)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = self.return_to


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

class KocinaApp(App):
    def build(self):
        self.title = "Kocina del Mundo"
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(CategoryScreen(name="category"))
        sm.add_widget(RecipeDetailScreen(name="detail"))
        sm.current = "home"
        return sm


if __name__ == "__main__":
    KocinaApp().run()