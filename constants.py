"""
Constantes y configuración de Kocina del Mundo.
"""

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "cambia_esta_clave"

# Dirección del blog (fuente real de las recetas)
BLOG_URL = "https://kocinadelmundo24.blogspot.com"

# Categorías principales tal como aparecen en el menú del sitio web.
# Cada una tiene sus subcategorías reales (usadas como labels en Blogger).
CATEGORIES = {
    "Entrantes": [
        "Ensaladas", "Sopas", "Cremas", "Tapas", "Aperitivos",
        "Bruschettas", "Salsas", "Guarniciones",
    ],
    "Principales": [
        "Pollo", "Carne", "Cerdo", "Cordero", "Pescado", "Mariscos",
        "Pasta", "Arroz", "Pizza", "Hamburguesas", "Comida Española",
        "Comida Italiana", "Comida Mexicana", "Comida Asiática",
        "Recetas Vegetarianas", "Recetas Saludables",
    ],
    "Postres": [
        "Tartas", "Cheesecake", "Flanes", "Brownies", "Galletas",
        "Muffins", "Chocolate", "Tiramisú", "Churros", "Postres sin horno",
    ],
    "Panaderia": [
        "Pan Casero", "Pan Integral", "Baguette", "Brioche",
        "Croissants", "Bollería", "Empanadas", "Masa para Pizza",
    ],
    "Bebidas": [
        "Zumos", "Batidos", "Smoothies", "Café", "Té",
        "Cócteles", "Limonadas", "Milkshakes",
    ],
    "Helados": [
        "Chocolate", "Vainilla", "Fresa", "Mango", "Coco",
        "Yogur Helado", "Sorbetes", "Helados sin Máquina",
    ],
}

# Paleta de color extraída del logo (misma que la web)
COLOR_BG = (0.98, 0.95, 0.89, 1)
COLOR_PRIMARY = (0.80, 0.33, 0.13, 1)
COLOR_PRIMARY_DARK = (0.58, 0.21, 0.08, 1)
COLOR_ACCENT = (0.35, 0.52, 0.29, 1)
COLOR_DANGER = (0.72, 0.20, 0.18, 1)
COLOR_TEXT = (0.20, 0.13, 0.09, 1)
COLOR_CARD = (1, 1, 1, 1)
COLOR_WHITE = (1, 1, 1, 1)