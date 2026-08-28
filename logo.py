"""
logo.py
Carga el logo real desde base64. Si por algún motivo falla,
main.py usa un texto de respaldo automáticamente.

IMPORTANTE: la textura NO se crea al importar este archivo. Crear una
textura (llamar a .texture) requiere que la ventana/contexto gráfico ya
esté listo. Hacerlo al importar el módulo (demasiado temprano en Android)
puede provocar un cierre nativo silencioso de la app. Por eso la carga
se hace de forma diferida, la primera vez que se llama a get_logo_texture().
"""

import base64
from io import BytesIO

from kivy.uix.image import Image as LogoImage
from kivy.metrics import dp

from logo_data import LOGO_BASE64

LOGO_WIDTH = dp(253)
LOGO_HEIGHT = dp(130)

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
        _logo_texture_cache = CoreImage(BytesIO(image_data), ext="png").texture
    except Exception:
        _logo_texture_cache = None
    return _logo_texture_cache