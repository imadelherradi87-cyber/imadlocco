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

MESES_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
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
    """Convierte '2026-07-22T10:00:00.000+02:00' en '22 de julio de 2026'."""
    if not published_iso:
        return ""
    try:
        cleaned = published_iso.split(".")[0].split("+")[0]
        dt = datetime.strptime(cleaned, "%Y-%m-%dT%H:%M:%S")
        return f"{dt.day} de {MESES_ES[dt.month - 1]} de {dt.year}"
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

    image_url = None
    if "media$thumbnail" in entry:
        image_url = entry["media$thumbnail"].get("url", "").replace("/s72-c/", "/s600/")
    if not image_url:
        image_url = _extract_first_image(content_html)

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

    def _on_success(request, result):
        try:
            if isinstance(result, (bytes, str)):
                result = json.loads(result)
            entries = result.get("feed", {}).get("entry", [])
            posts = [_parse_entry(e) for e in entries]
            on_success(posts)
        except Exception as e:
            if on_error:
                on_error(str(e))

    def _on_error(request, error):
        if on_error:
            on_error(str(error))

    def _on_failure(request, result):
        if on_error:
            on_error("request_failed")

    UrlRequest(
        url + params,
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