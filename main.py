"""
Kocina del Mundo
App nativa que refleja fielmente la estructura de
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
from kivy.uix.carousel import Carousel
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
# Helpers de UI
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


class Card(BoxLayout):
    def __init__(self, bg=COLOR_CARD, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*bg)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


def section_title(text):
    return autosize_label(text, font_size="19sp", bold=True, color=COLOR_PRIMARY_DARK, width_padding=dp(28))


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
    """Tarjeta compacta de receta: miniatura + título + categorías."""
    card = Card(orientation="horizontal", size_hint_y=None, height=dp(96),
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


def make_featured_slide(post, on_press):
    """Diapositiva grande del carrusel destacado (igual que la portada web)."""
    slide = BoxLayout(orientation="vertical", padding=dp(4), spacing=dp(6))

    if post.get("imagen"):
        img = AsyncImage(source=post["imagen"], size_hint=(1, 1), allow_stretch=True, keep_ratio=True)
    else:
        img = BoxLayout(size_hint=(1, 1))
    slide.add_widget(img)

    caption = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(90),
                         padding=(dp(12), dp(6)), spacing=dp(4))
    if post.get("fecha_es"):
        caption.add_widget(autosize_label(post["fecha_es"], font_size="12sp",
                                           color=COLOR_ACCENT, width_padding=dp(40)))
    caption.add_widget(autosize_label(post.get("titulo", ""), font_size="16sp", bold=True,
                                       color=COLOR_TEXT, width_padding=dp(40)))
    ver_btn = flat_button("Ver receta", COLOR_ACCENT, height=dp(36), font_size="12sp")
    ver_btn.size_hint_y = None
    ver_btn.bind(on_press=lambda i: on_press(post))
    caption.add_widget(ver_btn)
    slide.add_widget(caption)

    return slide


def loading_label(text="Cargando recetas..."):
    return Label(text=text, color=COLOR_TEXT, size_hint_y=None, height=dp(60), font_size="15sp")


def error_label(text="No se pudieron cargar las recetas. Revisa tu conexión."):
    return Label(text=text, color=COLOR_DANGER, size_hint_y=None, height=dp(60), font_size="14sp")


def make_about_section():
    box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8), padding=(0, dp(10)))
    box.bind(minimum_height=box.setter("height"))
    box.add_widget(section_title("Sobre Kocina del Mundo"))
    box.add_widget(autosize_label(
        "Bienvenido a Kocina del Mundo, un rincón digital para viajar a través "
        "del sabor: recetas caseras, técnicas tradicionales e historias de "
        "cocinas de todo el planeta, explicadas paso a paso.",
        font_size="14sp", width_padding=dp(28),
    ))
    return box


def make_footer():
    box = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(90),
                     padding=(dp(20), dp(14)), spacing=dp(6))
    with box.canvas.before:
        Color(*COLOR_PRIMARY_DARK)
        rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[0])
        box.bind(pos=lambda i, v: setattr(rect, "pos", v))
        box.bind(size=lambda i, v: setattr(rect, "size", v))
    box.add_widget(Label(text="Kocina del Mundo", bold=True, color=COLOR_WHITE, font_size="14sp",
                          size_hint_y=None, height=dp(24)))
    box.add_widget(Label(text="© Kocina del Mundo · Buen provecho", color=(1, 1, 1, 0.8),
                          font_size="11sp", size_hint_y=None, height=dp(20)))
    return box


# ---------------------------------------------------------------------------
# Home: portada con carrusel destacado, categorías, recetas y footer
# ---------------------------------------------------------------------------

class HomeScreen(Screen):
    def on_pre_enter(self, *args):
        self.build_ui()
        self.load_posts()

    def build_ui(self):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical")
        root.add_widget(make_header())

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

        self.body_scroll = ScrollView()
        self.body = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        self.body.bind(minimum_height=self.body.setter("height"))
        self.body.add_widget(loading_label())
        self.body_scroll.add_widget(self.body)
        root.add_widget(self.body_scroll)

        self.add_widget(root)

    def load_posts(self, query=None):
        self.body.clear_widgets()
        self.body.add_widget(loading_label())
        fetch_posts(self.show_posts, on_error=self.show_error, query=query, max_results=20)

    def show_posts(self, posts):
        self.body.clear_widgets()

        # Carrusel destacado (como la portada de la web)
        if posts:
            carousel = Carousel(direction="right", size_hint_y=None, height=dp(320))
            for post in posts[:5]:
                carousel.add_widget(make_featured_slide(post, self.open_detail))
            self.body.add_widget(carousel)

        results_wrap = BoxLayout(orientation="vertical", size_hint_y=None,
                                  spacing=dp(10), padding=dp(14))
        results_wrap.bind(minimum_height=results_wrap.setter("height"))
        results_wrap.add_widget(section_title(
            "Últimas recetas" if not posts else f"Últimas recetas ({len(posts)})"
        ))
        if not posts:
            results_wrap.add_widget(Label(
                text="No se encontraron recetas.", color=COLOR_TEXT,
                size_hint_y=None, height=dp(40),
            ))
        for post in posts:
            results_wrap.add_widget(make_recipe_card(post, self.open_detail))
        self.body.add_widget(results_wrap)

        about_wrap = BoxLayout(orientation="vertical", size_hint_y=None, padding=(dp(14), 0))
        about_wrap.bind(minimum_height=about_wrap.setter("height"))
        about_wrap.add_widget(make_about_section())
        self.body.add_widget(about_wrap)

        self.body.add_widget(make_footer())

    def show_error(self, err):
        self.body.clear_widgets()
        self.body.add_widget(error_label())

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
# Categoría: subcategorías reales + recetas filtradas
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
# Detalle de receta
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

        if post.get("fecha_es"):
            content.add_widget(autosize_label(post["fecha_es"], font_size="12sp", color=COLOR_ACCENT))

        if post.get("categorias"):
            content.add_widget(autosize_label(
                " · ".join(post["categorias"]), font_size="13sp", color=COLOR_ACCENT, bold=True,
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