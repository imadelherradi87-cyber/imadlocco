"""
blogger_api.py

Lee recetas directamente del blog público de Kocina del Mundo
usando el feed JSON de Blogger (no requiere API key para blogs públicos).
"""

import re
import json
from datetime import datetime
from urllib.parse import quote
from kivy.network.urlrequest import UrlRequest

from constants import BLOG_URL

FEED_URL = f"{BLOG_URL}/feeds/posts/default"

MONTHS_EN = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

# Rango de puntos de código que cubre la mayoría de emojis/pictogramas.
# El tipo de letra por defecto de Kivy no los soporta y los muestra como □.
_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U0001F1E6-\U0001F1FF"
    "\U00002190-\U000021FF"
    "\U00002B00-\U00002BFF"
    "\uFE0F"
    "]+",
    flags=re.UNICODE,
)


def _strip_emoji(text):
    if not text:
        return text
    return _EMOJI_PATTERN.sub("", text)


def _resize_image_url(url, size=640):
    """Pide una versión más pequeña de la imagen al CDN de Blogger/Google,
    en vez de descargar la foto original a resolución completa. Esto
    acelera mucho la carga sin perder calidad visible en el teléfono."""
    if not url:
        return url
    # Patrón clásico de Blogger: /s1600/ , /s72-c/ , etc.
    new_url = re.sub(r"/s\d+(-c)?/", f"/s{size}/", url)
    if new_url != url:
        return new_url
    # Patrón más nuevo (googleusercontent) con '=': ...=s1600 o ...=w1200-h800
    new_url = re.sub(r"=s\d+(-c)?(-rw)?$", f"=s{size}", url)
    if new_url != url:
        return new_url
    new_url = re.sub(r"=w\d+-h\d+(-c)?(-rw)?$", f"=s{size}", url)
    if new_url != url:
        return new_url
    return url


def _extract_first_image(html_content):
    if not html_content:
        return None
    match = re.search(r'<img[^>]+src="([^"]+)"', html_content)
    return match.group(1) if match else None


def _strip_html(html_content):
    if not html_content:
        return ""
    text = re.sub(r"<br\s*/?>", "\n", html_content)
    text = re.sub(r"</p>", "\n\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    text = text.replace("&quot;", '"').replace("&#39;", "'")
    text = _strip_emoji(text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def format_date_es(published_iso):
    """Converts '2026-07-22T10:00:00.000+02:00' into 'July 22, 2026'."""
    if not published_iso:
        return ""
    try:
        cleaned = published_iso.split(".")[0].split("+")[0]
        dt = datetime.strptime(cleaned, "%Y-%m-%dT%H:%M:%S")
        return f"{MONTHS_EN[dt.month - 1]} {dt.day}, {dt.year}"
    except Exception:
        return ""


def _parse_entry(entry):
    title = _strip_emoji(entry.get("title", {}).get("$t", "Sin título"))
    content_html = entry.get("content", {}).get("$t", "")
    post_id = entry.get("id", {}).get("$t", "")

    link = ""
    for l in entry.get("link", []):
        if l.get("rel") == "alternate":
            link = l.get("href", "")
            break

    labels = [c.get("term") for c in entry.get("category", []) if c.get("term")]

    image_url = _extract_first_image(content_html)
    if not image_url and "media$thumbnail" in entry:
        # Como último recurso, usa la miniatura pero pide un tamaño más grande
        thumb_url = entry["media$thumbnail"].get("url", "")
        image_url = re.sub(r"/s\d+(-c)?/", "/s600/", thumb_url) if thumb_url else None

    published = entry.get("published", {}).get("$t", "")

    return {
        "id": post_id,
        "titulo": title,
        "link": link,
        "categorias": labels,
        "imagen": image_url,
        "contenido_html": content_html,
        "contenido_texto": _strip_html(content_html),
        "fecha": published,
        "fecha_es": format_date_es(published),
    }


def fetch_posts(on_success, on_error=None, label=None, query=None, max_results=20):
    url = FEED_URL
    if label:
        url += f"/-/{quote(label)}"

    params = f"?alt=json&max-results={max_results}"
    if query:
        params += f"&q={quote(query)}"

    full_url = url + params

    def _on_success(request, result):
        try:
            if isinstance(result, (bytes, str)):
                result = json.loads(result)
            entries = result.get("feed", {}).get("entry", [])
            posts = [_parse_entry(e) for e in entries]
            on_success(posts)
        except Exception as e:
            if on_error:
                on_error(f"{type(e).__name__}: {e}")

    def _on_error(request, error):
        if on_error:
            on_error(f"{type(error).__name__}: {error}")

    def _on_failure(request, result):
        if on_error:
            status = getattr(request, "resp_status", "sin respuesta")
            on_error(f"HTTP {status} al pedir {full_url}")

    UrlRequest(
        full_url,
        on_success=_on_success,
        on_error=_on_error,
        on_failure=_on_failure,
        timeout=15,
    )


def fetch_single_post(post_link, on_success, on_error=None):
    def _on_success(posts):
        match = next((p for p in posts if p["link"] == post_link), None)
        if match:
            on_success(match)
        elif on_error:
            on_error("not_found")

    fetch_posts(_on_success, on_error=on_error, max_results=50)
