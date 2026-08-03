"""
icons.py
Carga los iconos de categoría (Entrantes, Principales, Postres, Panaderia,
Bebidas, Helados) desde base64, tal como aparecen en el menú del sitio web.
"""

import base64
from io import BytesIO

from kivy.core.image import Image as CoreImage

from icons_data import CATEGORY_ICONS_BASE64

CATEGORY_ICON_TEXTURES = {}

for _name, _b64 in CATEGORY_ICONS_BASE64.items():
    try:
        _data = base64.b64decode(_b64)
        CATEGORY_ICON_TEXTURES[_name] = CoreImage(BytesIO(_data), ext="png").texture
    except Exception:
        CATEGORY_ICON_TEXTURES[_name] = None

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
    return CATEGORY_ICON_TEXTURES.get(key)
