"""
logo.py
Carga el logo real desde base64. Si por algún motivo falla,
main.py usa un texto de respaldo automáticamente.
"""

import base64
from io import BytesIO

from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image as LogoImage
from kivy.metrics import dp

from logo_data import LOGO_BASE64

LOGO_TEXTURE = None
LOGO_WIDTH = dp(195)
LOGO_HEIGHT = dp(130)

if LOGO_BASE64:
    try:
        image_data = base64.b64decode(LOGO_BASE64)
        LOGO_TEXTURE = CoreImage(BytesIO(image_data), ext="png").texture
    except Exception:
        LOGO_TEXTURE = None