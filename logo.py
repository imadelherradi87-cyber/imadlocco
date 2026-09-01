"""
logo.py
Loads the real logo from base64. If it fails for any reason,
main.py automatically falls back to a text label.

IMPORTANT: the texture is NOT created at import time. Creating a
texture (calling .texture) requires the graphics window/context to
already be ready. Doing this at module import time (too early on
Android) can cause a silent native crash. That's why loading is
deferred until the first call to get_logo_texture().
"""

import base64
from io import BytesIO

from kivy.uix.image import Image as LogoImage
from kivy.metrics import dp

from logo_data import LOGO_BASE64

LOGO_WIDTH = dp(253)
LOGO_HEIGHT = dp(136)  # aspect ratio ~1.86 (600x322 px)

_logo_texture_cache = None
_logo_load_attempted = False


def get_logo_texture():
    global _logo_texture_cache, _logo_load_attempted
    if _logo_texture_cache is not None:
        return _logo_texture_cache
    if _logo_load_attempted:
        return None
    _logo_load_attempted = True
    if not LOGO_BASE64:
        return None
    try:
        from kivy.core.image import Image as CoreImage
        image_data = base64.b64decode(LOGO_BASE64)
        _logo_texture_cache = CoreImage(BytesIO(image_data), ext="jpg").texture
    except Exception:
        _logo_texture_cache = None
    return _logo_texture_cache