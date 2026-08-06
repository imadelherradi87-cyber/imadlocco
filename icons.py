"""
icons.py
Carga los iconos de categoría (Entrantes, Principales, Postres, Panaderia,
Bebidas, Helados) desde base64, tal como aparecen en el menú del sitio web.

IMPORTANTE: las texturas NO se crean al importar este archivo (ver la
misma nota en logo.py) — se crean de forma diferida, la primera vez que
se pide cada icono, para evitar un cierre nativo silencioso en Android.
"""

import base64
from io import BytesIO

from icons_data import CATEGORY_ICONS_BASE64

_texture_cache = {}
_load_attempted = {}

# Relaciona cada categoría principal con su clave de icono.
CATEGORY_ICON_KEYS = {
    "Entrantes": "entrantes",
    "Principales": "principales",
    "Postres": "postres",
    "Panaderia": "panaderia",
    "Bebidas": "bebidas",
    "Helados": "helados",
}


def get_icon_texture(category_name):
    key = CATEGORY_ICON_KEYS.get(category_name)
    if not key:
        return None
    if key in _texture_cache:
        return _texture_cache[key]
    if _load_attempted.get(key):
        return None
    _load_attempted[key] = True

    b64 = CATEGORY_ICONS_BASE64.get(key)
    if not b64:
        return None
    try:
        from kivy.core.image import Image as CoreImage
        data = base64.b64decode(b64)
        texture = CoreImage(BytesIO(data), ext="png").texture
        _texture_cache[key] = texture
        return texture
    except Exception:
        return None
