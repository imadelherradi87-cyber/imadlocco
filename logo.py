"""
Manejo del logo de la app (cargado desde logo_data.py en base64).
"""

import base64
import io

from kivy.core.image import Image as CoreImage
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from kivy.uix.widget import Widget


def _load_logo_texture():
    try:
        from logo_data import HEADER_LOGO_BASE64
        raw = base64.b64decode(HEADER_LOGO_BASE64)
        buf = io.BytesIO(raw)
        core_img = CoreImage(buf, ext="png")
        return core_img.texture
    except Exception:
        return None


LOGO_TEXTURE = _load_logo_texture()
LOGO_HEIGHT = dp(44)
LOGO_WIDTH = dp(66)
if LOGO_TEXTURE:
    ratio = LOGO_TEXTURE.width / LOGO_TEXTURE.height
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