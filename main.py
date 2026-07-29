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
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import AsyncImage, Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.carousel import Carousel
from kivy.uix.stencilview import StencilView
from kivy.graphics import Color, RoundedRectangle, Ellipse, Line

from constants import (
    CATEGORIES, BLOG_URL,
    COLOR_BG, COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_ACCENT,
    COLOR_DANGER, COLOR_TEXT, COLOR_CARD, COLOR_WHITE,
)

Window.clearcolor = COLOR_BG

from logo import LOGO_TEXTURE, LOGO_HEIGHT, LOGO_WIDTH, LogoImage
from icons import get_icon_texture
from blogger_api import fetch_posts


# ---------------------------------------------------------------------------
# Helpers de UI
# ---------------------------------------------------------------------------

class RoundButton(ButtonBehavior, BoxLayout):
    """Botón rectangular con esquinas redondeadas (round rectangle), color naranja."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self._color_instr = Color(*COLOR_PRIMARY)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
        self.bind(pos=self._update_rect, size=self._update_rect)
        self._label = Label(bold=True)
        self.add_widget(self._label)

    def _update_rect(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size


def flat_button(text, bg_color=None, text_color=COLOR_WHITE, height=dp(50), font_size="16sp", bold=True):
    """Crea un botón round-rectangle naranja (bg_color se ignora a propósito:
    todos los botones del sitio usan el mismo estilo naranja)."""
    btn = RoundButton(size_hint_y=None, height=height)
    btn._label.text = text
    btn._label.color = text_color
    btn._label.font_size = font_size
    btn._label.bold = bold
    return btn


def autosize_label(text, markup=False, font_size="15sp", color=COLOR_TEXT, bold=False,
                    width_padding=dp(24), halign="left"):
    lbl = Label(
        text=text, markup=markup, font_size=font_size, color=color, bold=bold,
        size_hint_y=None, halign=halign, valign="top",
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


def make_header():
    header = BoxLayout(size_hint_y=None, height=LOGO_HEIGHT, padding=(dp(8), 0))
    with header.canvas.before:
        Color(1, 1, 1, 1)
        rect = RoundedRectangle(pos=header.pos, size=header.size, radius=[0])
        header.bind(pos=lambda i, v: setattr(rect, "pos", v))
        header.bind(size=lambda i, v: setattr(rect, "size", v))

    from kivy.uix.anchorlayout import AnchorLayout
    logo_anchor = AnchorLayout(anchor_x="center", anchor_y="center")
    if LOGO_TEXTURE:
        logo = LogoImage(texture=LOGO_TEXTURE, size_hint=(None, None),
                          width=LOGO_WIDTH, height=LOGO_HEIGHT)
    else:
        logo = Label(text="Kocina del Mundo", font_size="22sp", bold=True, color=COLOR_PRIMARY)
    logo_anchor.add_widget(logo)
    header.add_widget(logo_anchor)
    return header


def make_back_row(on_back):
    row = BoxLayout(size_hint_y=None, height=dp(40), padding=(dp(8), dp(4)))
    back_btn = flat_button("< Volver", height=dp(32), font_size="12sp")
    back_btn.size_hint_x = None
    back_btn.width = dp(90)
    if on_back:
        back_btn.bind(on_press=on_back)
    row.add_widget(back_btn)
    return row


def make_detail_back_row(on_back):
    """Barra de regreso para la pantalla de detalle: fondo negro, botón
    blanco con texto negro, solo la palabra 'Volver' sin flecha."""
    row = BoxLayout(size_hint_y=None, height=dp(48), padding=(dp(10), dp(6)))
    with row.canvas.before:
        Color(0, 0, 0, 1)
        rect = RoundedRectangle(pos=row.pos, size=row.size, radius=[0])
        row.bind(pos=lambda i, v: setattr(rect, "pos", v))
        row.bind(size=lambda i, v: setattr(rect, "size", v))

    back_btn = RoundButton(size_hint=(None, None), width=dp(90), height=dp(34))
    back_btn._color_instr.rgba = (1, 1, 1, 1)
    back_btn._label.text = "Volver"
    back_btn._label.color = (0, 0, 0, 1)
    back_btn._label.font_size = "12sp"
    if on_back:
        back_btn.bind(on_press=on_back)
    row.add_widget(back_btn)
    return row


def make_category_row(on_category):
    """Fila de iconos de categoría con fondo negro, reutilizada en todas las pantallas."""
    cat_row = BoxLayout(size_hint_y=None, height=dp(64), padding=(dp(6), dp(4)), spacing=dp(4))
    with cat_row.canvas.before:
        Color(0, 0, 0, 1)
        rect = RoundedRectangle(pos=cat_row.pos, size=cat_row.size, radius=[0])
        cat_row.bind(pos=lambda i, v: setattr(rect, "pos", v))
        cat_row.bind(size=lambda i, v: setattr(rect, "size", v))
    for cat_name in CATEGORIES.keys():
        btn = CategoryButton(cat_name, icon_texture=get_icon_texture(cat_name), size_hint_x=1)
        btn.bind(on_press=lambda inst, name=cat_name: on_category(name))
        cat_row.add_widget(btn)
    return cat_row


def make_full_top_nav(on_category, show_back=False, on_back=None, detail_mode=False):
    """Encabezado completo (igual estilo que la portada) reutilizado en todas las pantallas:
    barra de aviso, logo y menú de categorías con fondo negro."""
    wrap = BoxLayout(orientation="vertical", size_hint_y=None)
    wrap.bind(minimum_height=wrap.setter("height"))
    if show_back:
        if detail_mode:
            wrap.add_widget(make_detail_back_row(on_back))
        else:
            wrap.add_widget(make_back_row(on_back))
    if not detail_mode:
        wrap.add_widget(make_tagline_bar())
    wrap.add_widget(make_header())
    wrap.add_widget(make_category_row(on_category))
    return wrap


class RoundedImageBox(ButtonBehavior, StencilView):
    """Contenedor que recorta una imagen en un rectángulo con esquinas
    redondeadas. StencilView no distribuye hijos automáticamente, así que
    aquí ajustamos manualmente la posición/tamaño de la imagen."""

    def __init__(self, radius=dp(14), **kwargs):
        super().__init__(**kwargs)
        self._radius = radius
        self._child_img = None
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size
        if self._child_img is not None:
            self._child_img.pos = self.pos
            self._child_img.size = self.size

    def set_image(self, source):
        if self._child_img is not None:
            self.remove_widget(self._child_img)
            self._child_img = None
        if source:
            img = AsyncImage(source=source, allow_stretch=True, keep_ratio=False,
                              pos=self.pos, size=self.size)
            self.add_widget(img)
            self._child_img = img


class CircleArrowButton(ButtonBehavior, BoxLayout):
    """Botón circular naranja con una flecha, para abrir la receta."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*COLOR_PRIMARY)
            self._circle = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self._update_circle, size=self._update_circle)
        self.add_widget(Label(text=">", bold=True, color=COLOR_WHITE, font_size="18sp"))

    def _update_circle(self, *args):
        self._circle.pos = self.pos
        self._circle.size = self.size


def make_recipe_card(post, on_press):
    """Tarjeta grande de receta: imagen redondeada + título + extracto + botón circular."""
    card = Card(orientation="horizontal", size_hint_y=None, height=dp(120),
                padding=dp(10), spacing=dp(12))

    image_box = RoundedImageBox(size_hint=(None, None), size=(dp(100), dp(100)))
    image_box.set_image(post.get("imagen"))
    image_box.bind(on_press=lambda i: on_press(post))
    card.add_widget(image_box)

    info = BoxLayout(orientation="vertical", spacing=dp(4))

    title_lbl = Label(
        text=post.get("titulo", ""), font_size="15sp", bold=True, color=COLOR_TEXT,
        halign="left", valign="top", shorten=True, shorten_from="right",
        size_hint_y=None, height=dp(40),
    )
    title_lbl.bind(size=lambda inst, val: setattr(inst, "text_size", val))
    info.add_widget(title_lbl)

    excerpt_text = (post.get("contenido_texto") or "").strip().replace("\n", " ")
    if len(excerpt_text) > 90:
        excerpt_text = excerpt_text[:90].rstrip() + "…"
    excerpt_lbl = Label(
        text=excerpt_text, font_size="12sp", color=COLOR_TEXT,
        halign="left", valign="top", shorten=True,
        size_hint_y=1,
    )
    excerpt_lbl.bind(size=lambda inst, val: setattr(inst, "text_size", val))
    info.add_widget(excerpt_lbl)
    card.add_widget(info)

    arrow_btn = CircleArrowButton(size_hint=(None, None), size=(dp(38), dp(38)))
    arrow_btn.bind(on_press=lambda i: on_press(post))
    card.add_widget(arrow_btn)

    return card


def make_featured_slide(post, on_press):
    """Diapositiva grande del carrusel destacado (igual que la portada web)."""
    slide = BoxLayout(orientation="vertical", padding=(dp(12), dp(10)), spacing=dp(8))

    image_box = RoundedImageBox(size_hint=(1, 1))
    image_box.set_image(post.get("imagen"))
    image_box.bind(on_press=lambda i: on_press(post))
    slide.add_widget(image_box)

    caption = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(90), spacing=dp(4))
    if post.get("fecha_es"):
        caption.add_widget(autosize_label(post["fecha_es"], font_size="12sp",
                                           color=COLOR_WHITE, width_padding=dp(40)))
    caption.add_widget(autosize_label(post.get("titulo", ""), font_size="16sp", bold=True,
                                       color=COLOR_WHITE, width_padding=dp(40)))
    ver_btn = flat_button("Ver receta", height=dp(36), font_size="12sp")
    ver_btn.size_hint_y = None
    ver_btn.bind(on_press=lambda i: on_press(post))
    caption.add_widget(ver_btn)
    slide.add_widget(caption)

    return slide


def make_tagline_bar():
    bar = BoxLayout(size_hint_y=None, height=dp(30))
    with bar.canvas.before:
        Color(0, 0, 0, 1)
        rect = RoundedRectangle(pos=bar.pos, size=bar.size, radius=[0])
        bar.bind(pos=lambda i, v: setattr(rect, "pos", v))
        bar.bind(size=lambda i, v: setattr(rect, "size", v))
    bar.add_widget(Label(
        text="NUEVAS RECETAS CADA HORA, PARA TI Y TU FAMILIA",
        font_size="11sp", color=COLOR_WHITE, bold=True,
    ))
    return bar


class CategoryButton(ButtonBehavior, BoxLayout):
    """Botón circular de categoría con icono + texto pequeño, como el menú del sitio."""

    def __init__(self, text, icon_texture=None, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(2), **kwargs)
        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.bg_circle = Ellipse(pos=self.pos, size=(0, 0))
            Color(1, 1, 1, 1)
            self.bg_circle_outline = Line(circle=(0, 0, 0), width=dp(1.2))
        self.bind(pos=self._update_circle, size=self._update_circle)

        circle_wrap = BoxLayout(size_hint_y=None, height=dp(40))
        if icon_texture:
            icon = Image(texture=icon_texture, size_hint=(None, None), size=(dp(24), dp(24)))
            icon.pos_hint = {"center_x": 0.5, "center_y": 0.5}
            icon_anchor = _center_anchor(icon)
            circle_wrap.add_widget(icon_anchor)
        self.add_widget(circle_wrap)

        self.add_widget(Label(text=text, font_size="9sp", bold=True, color=COLOR_WHITE,
                               size_hint_y=None, height=dp(14), shorten=True))

    def _update_circle(self, *args):
        diameter = dp(40)
        cx = self.center_x
        cy = self.pos[1] + self.height - dp(20)
        self.bg_circle.pos = (cx - diameter / 2, cy - diameter / 2)
        self.bg_circle.size = (diameter, diameter)
        self.bg_circle_outline.circle = (cx, cy, diameter / 2)


def _center_anchor(widget):
    from kivy.uix.anchorlayout import AnchorLayout
    anchor = AnchorLayout(anchor_x="center", anchor_y="center")
    anchor.add_widget(widget)
    return anchor


class RoundedInputWrap(BoxLayout):
    """Fondo blanco redondeado detrás de un TextInput transparente (round rectangle)."""

    def __init__(self, radius=dp(22), bg_color=COLOR_CARD, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size


def loading_label(text="Cargando recetas..."):
    return Label(text=text, color=COLOR_TEXT, size_hint_y=None, height=dp(60), font_size="15sp")


def error_label(text="No se pudieron cargar las recetas. Revisa tu conexión."):
    return Label(text=text, color=COLOR_DANGER, size_hint_y=None, height=dp(60), font_size="14sp")


def make_about_section():
    box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8), padding=(0, dp(10)))
    box.bind(minimum_height=box.setter("height"))

    box.add_widget(autosize_label(
        "Sobre Kocina del Mundo", font_size="19sp", bold=True,
        color=COLOR_PRIMARY_DARK, width_padding=dp(28), halign="center",
    ))
    box.add_widget(autosize_label(
        "Bienvenido a Kocina del Mundo, un rincón digital para viajar a través "
        "del sabor: recetas caseras, técnicas tradicionales e historias de "
        "cocinas de todo el planeta, explicadas paso a paso.",
        font_size="14sp", width_padding=dp(28), halign="center",
    ))
    return box


def make_footer():
    box = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(56),
                     padding=(dp(20), dp(14)), spacing=dp(6))
    with box.canvas.before:
        Color(0, 0, 0, 1)
        rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[0])
        box.bind(pos=lambda i, v: setattr(rect, "pos", v))
        box.bind(size=lambda i, v: setattr(rect, "size", v))
    box.add_widget(Label(text="@kocina del mundo. Buen provechi", color=COLOR_WHITE,
                          font_size="12sp", size_hint_y=None, height=dp(24)))
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
        root.add_widget(make_full_top_nav(self.open_category_by_name))

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

        # Carrusel destacado (como la portada de la web) con fondo negro
        if posts:
            carousel_wrap = BoxLayout(size_hint_y=None, height=dp(320))
            with carousel_wrap.canvas.before:
                Color(0, 0, 0, 1)
                rect = RoundedRectangle(pos=carousel_wrap.pos, size=carousel_wrap.size, radius=[0])
                carousel_wrap.bind(pos=lambda i, v: setattr(rect, "pos", v))
                carousel_wrap.bind(size=lambda i, v: setattr(rect, "size", v))
            carousel = Carousel(direction="right", size_hint_y=None, height=dp(320))
            for post in posts[:5]:
                carousel.add_widget(make_featured_slide(post, self.open_detail))
            carousel_wrap.add_widget(carousel)
            self.body.add_widget(carousel_wrap)

        # Búsqueda (colocada debajo de la primera receta destacada)
        search_bar = BoxLayout(size_hint_y=None, height=dp(50), padding=dp(10), spacing=dp(8))
        input_wrap = RoundedInputWrap(radius=dp(22), size_hint_x=1)
        self.search_input = TextInput(
            hint_text="Buscar recetas...", multiline=False,
            background_normal="", background_active="", background_color=(0, 0, 0, 0),
            foreground_color=COLOR_TEXT, hint_text_color=(0.45, 0.42, 0.38, 1),
            cursor_color=COLOR_TEXT, padding=[dp(16), dp(12)],
        )
        self.search_input.bind(on_text_validate=self.do_search)
        input_wrap.add_widget(self.search_input)
        search_btn = flat_button("Buscar", height=dp(44), font_size="13sp")
        search_btn.size_hint_x = None
        search_btn.width = dp(90)
        search_btn.bind(on_press=self.do_search)
        search_bar.add_widget(input_wrap)
        search_bar.add_widget(search_btn)
        self.body.add_widget(search_bar)

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

    def open_category_by_name(self, category_name):
        cat_screen = self.manager.get_screen("category")
        cat_screen.set_category(category_name)
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "category"

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
        root.add_widget(make_full_top_nav(self.open_category_by_name, show_back=True, on_back=self.go_back))

        title_row = BoxLayout(size_hint_y=None, height=dp(40), padding=(dp(20), 0), spacing=dp(8))
        icon_tex = get_icon_texture(self.current_category)
        if icon_tex:
            title_row.add_widget(Image(texture=icon_tex, size_hint=(None, None), size=(dp(28), dp(28))))
        title_row.add_widget(autosize_label(
            self.current_category or "", font_size="20sp", bold=True,
            color=COLOR_PRIMARY_DARK, width_padding=dp(60),
        ))
        root.add_widget(title_row)

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

    def open_category_by_name(self, category_name):
        self.set_category(category_name)

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
        root.add_widget(make_full_top_nav(self.open_category_by_name, show_back=True,
                                           on_back=self.go_back, detail_mode=True))

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
            content.add_widget(autosize_label(post["fecha_es"], font_size="12sp", color=COLOR_PRIMARY_DARK))

        if post.get("categorias"):
            content.add_widget(autosize_label(
                " · ".join(post["categorias"]), font_size="13sp", color=COLOR_PRIMARY_DARK, bold=True,
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

    def open_category_by_name(self, category_name):
        cat_screen = self.manager.get_screen("category")
        cat_screen.set_category(category_name)
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "category"

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