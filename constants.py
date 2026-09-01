"""
Constants and configuration for Recipes Method.
"""

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "cambia_esta_clave"

# Blog address (real source of the recipes)
BLOG_URL = "https://recipesmethod24.blogspot.com"

# Main categories exactly as they exist as Blogger post labels.
# IMPORTANT: these values must stay unchanged (in Spanish) because they
# are used to filter posts by label when talking to the Blogger feed.
# See CATEGORY_LABELS_EN below for the English text shown to the user.
CATEGORIES = {
    "Bebidas": [
        "Zumos", "Batidos", "Smoothies", "Café", "Té",
        "Cócteles", "Limonadas", "Milkshakes",
    ],
    "Principales": [
        "Pollo", "Carne", "Cerdo", "Cordero", "Pescado", "Mariscos",
        "Pasta", "Arroz", "Pizza", "Hamburguesas", "Comida Española",
        "Comida Italiana", "Comida Mexicana", "Comida Asiática",
        "Recetas Vegetarianas", "Recetas Saludables",
    ],
    "Entrantes": [
        "Ensaladas", "Sopas", "Cremas", "Tapas", "Aperitivos",
        "Bruschettas", "Salsas", "Guarniciones",
    ],
    "Postres": [
        "Tartas", "Cheesecake", "Flanes", "Brownies", "Galletas",
        "Muffins", "Chocolate", "Tiramisú", "Churros", "Postres sin horno",
    ],
    "Helados": [
        "Chocolate", "Vainilla", "Fresa", "Mango", "Coco",
        "Yogur Helado", "Sorbetes", "Helados sin Máquina",
    ],
    "Panaderia": [
        "Pan Casero", "Pan Integral", "Baguette", "Brioche",
        "Croissants", "Bollería", "Empanadas", "Masa para Pizza",
    ],
}

# English text shown on screen for each Spanish category/label above.
# Used only for display -- the app still queries Blogger using the
# original Spanish keys from CATEGORIES so filtering keeps working.
CATEGORY_LABELS_EN = {
    "Bebidas": "Drinks",
    "Principales": "Main Dishes",
    "Entrantes": "Starters",
    "Postres": "Desserts",
    "Helados": "Ice Cream",
    "Panaderia": "Bakery",

    "Zumos": "Juices", "Batidos": "Shakes", "Smoothies": "Smoothies",
    "Café": "Coffee", "Té": "Tea", "Cócteles": "Cocktails",
    "Limonadas": "Lemonades", "Milkshakes": "Milkshakes",

    "Pollo": "Chicken", "Carne": "Beef", "Cerdo": "Pork",
    "Cordero": "Lamb", "Pescado": "Fish", "Mariscos": "Seafood",
    "Pasta": "Pasta", "Arroz": "Rice", "Pizza": "Pizza",
    "Hamburguesas": "Burgers", "Comida Española": "Spanish Food",
    "Comida Italiana": "Italian Food", "Comida Mexicana": "Mexican Food",
    "Comida Asiática": "Asian Food",
    "Recetas Vegetarianas": "Vegetarian Recipes",
    "Recetas Saludables": "Healthy Recipes",

    "Ensaladas": "Salads", "Sopas": "Soups", "Cremas": "Creamy Soups",
    "Tapas": "Tapas", "Aperitivos": "Appetizers",
    "Bruschettas": "Bruschettas", "Salsas": "Sauces",
    "Guarniciones": "Side Dishes",

    "Tartas": "Cakes", "Cheesecake": "Cheesecake", "Flanes": "Flans",
    "Brownies": "Brownies", "Galletas": "Cookies", "Muffins": "Muffins",
    "Chocolate": "Chocolate", "Tiramisú": "Tiramisu",
    "Churros": "Churros", "Postres sin horno": "No-Bake Desserts",

    "Vainilla": "Vanilla", "Fresa": "Strawberry", "Mango": "Mango",
    "Coco": "Coconut", "Yogur Helado": "Frozen Yogurt",
    "Sorbetes": "Sorbets", "Helados sin Máquina": "No-Machine Ice Cream",

    "Pan Casero": "Homemade Bread", "Pan Integral": "Whole Wheat Bread",
    "Baguette": "Baguette", "Brioche": "Brioche",
    "Croissants": "Croissants", "Bollería": "Pastries",
    "Empanadas": "Empanadas", "Masa para Pizza": "Pizza Dough",
}

# Color palette extracted from the logo
COLOR_BG = (0.98, 0.95, 0.89, 1)
COLOR_PRIMARY = (0.80, 0.33, 0.13, 1)
COLOR_PRIMARY_DARK = (0.58, 0.21, 0.08, 1)
COLOR_ACCENT = (0.35, 0.52, 0.29, 1)
COLOR_DANGER = (0.72, 0.20, 0.18, 1)
COLOR_TEXT = (0.20, 0.13, 0.09, 1)
COLOR_CARD = (1, 1, 1, 1)
COLOR_WHITE = (1, 1, 1, 1)
