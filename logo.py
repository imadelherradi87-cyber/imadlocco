"""
logo.py
Carga el logo desde base64 si está disponible; si no, main.py usa un
texto de respaldo automáticamente.
"""

import base64
from io import BytesIO

from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image as LogoImage
from kivy.metrics import dp

from logo_data import LOGO_BASE64

LOGO_TEXTURE = None
LOGO_WIDTH = dp(140)
LOGO_HEIGHT = dp(44)

if LOGO_BASE64:
    try:
        image_data = base64.b64decode(LOGO_BASE64)
        LOGO_TEXTURE = CoreImage(BytesIO(image_data), ext="png").texture
    except Exception:
        LOGO_TEXTURE = None