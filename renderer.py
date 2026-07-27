from __future__ import annotations

import asyncio
import html
import re
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from playwright.async_api import async_playwright
from pydantic import ValidationError

from schema import Post

ROOT = Path(__file__).resolve().parent
POSTS = ROOT / "posts"
TEMPLATES = ROOT / "templates"
STYLES = ROOT / "styles"
OUTPUT = ROOT / "output"
CONFIG = ROOT / "config.yaml"

LANGS = [
    ("chinese", "zh"),
    ("japanese", "ja"),
    ("german", "de"),
]


def post_path(number: int) -> Path:
    return POSTS / f"{number:03d}.yaml"


def load_post(number: int) -> Post:
    path = post_path(number)
    if not path.exists():
        raise FileNotFoundError(f"Post not found: {path}")

    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}

    raw["project"] = config.get("project", raw.get("project", {}))
    language_cfg = config.get("languages", {})
    raw["labels"] = {
        key: language_cfg.get(key, {}).get("label", default)
        for key, default in {
            "english": "ENGLISH",
            "chinese": "中文",
            "japanese": "日本語",
            "german": "DEUTSCH",
        }.items()
    }

    try:
        return Post.model_validate(raw)
    except ValidationError as exc:
        raise ValueError(f"Invalid YAML in {path}:\n{exc}") from exc


def text_size_class(text: str) -> str:
    n = len(text.strip())
    if n <= 35:
        return "text-short"
    if n <= 85:
        return "text-medium"
    return "text-long"


def render_plain_tokens(tokens) -> str:
    parts = []
    for token in tokens:
        value = html.escape(token.text)
        if token.highlight:
            value = f"<mark>{value}</mark>"
        parts.append(f'<span class="sentence-token">{value}</span>')
    return "".join(parts)


def render_japanese_tokens(tokens) -> str:
    parts = []
    for token in tokens:
        value = html.escape(token.text)
        if token.highlight:
            value = f"<mark>{value}</mark>"

        # Important: ruby exists ONLY for tokens with kana.
        # No kana => no ruby/rt => no placeholder vertical gap.
        if token.kana:
            value = f'<ruby>{value}<rt>{html.escape(token.kana)}</rt></ruby>'

        parts.append(f'<span class="sentence-token">{value}</span>')
    return "".join(parts)


def env() -> Environment:
    e = Environment(
        loader=FileSystemLoader(TEMPLATES),
        autoescape=select_autoescape(["html", "xml"]),
    )
    e.filters["sizeclass"] = text_size_class
    e.filters["plain_tokens"] = render_plain_tokens
    e.filters["japanese_tokens"] = render_japanese_tokens
    return e


def render_html_files(post: Post) -> list[tuple[str, Path]]:
    out = OUTPUT / f"{post.number:03d}"
    out.mkdir(parents=True, exist_ok=True)

    css = (STYLES / "base.css").read_text(encoding="utf-8")
    jinja = env()

    slides = [("01-cover", "cover.html", {"post": post, "css": css})]

    for index, (attr, code) in enumerate(LANGS, start=2):
        slides.append((
            f"{index:02d}-{attr}",
            "language.html",
            {
                "post": post,
                "language": getattr(post, attr),
                "lang_key": attr,
                "lang_code": code,
                "css": css,
            },
        ))

    slide_num = 5
    if post.connection and post.connection.has_content():
        slides.append((f"{slide_num:02d}-connections", "connections.html", {"post": post, "css": css}))
        slide_num += 1

    if post.field_note and post.field_note.strip():
        slides.append((f"{slide_num:02d}-field-note", "field-note.html", {"post": post, "css": css}))

    rendered = []
    for stem, template, context in slides:
        body = jinja.get_template(template).render(**context)
        path = out / f"{stem}.html"
        path.write_text(body, encoding="utf-8")
        rendered.append((stem, path))

    preview = jinja.get_template("preview.html").render(
        post=post,
        slides=[(stem, path.name) for stem, path in rendered],
    )
    (out / "preview.html").write_text(preview, encoding="utf-8")
    return rendered


async def screenshot_post(post: Post) -> list[Path]:
    html_files = render_html_files(post)
    out_paths = []

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": 1080, "height": 1350},
            device_scale_factor=1,
        )
        for stem, source in html_files:
            await page.goto(source.resolve().as_uri(), wait_until="networkidle")
            await page.evaluate("document.fonts.ready")
            target = source.with_suffix(".png")
            await page.screenshot(path=str(target), full_page=False)
            out_paths.append(target)
        await browser.close()

    return out_paths


def render_one(number: int, screenshots: bool = True) -> list[Path]:
    post = load_post(number)
    if screenshots:
        return asyncio.run(screenshot_post(post))
    return [path for _, path in render_html_files(post)]


def existing_numbers() -> list[int]:
    nums = []
    for path in POSTS.glob("[0-9][0-9][0-9].yaml"):
        m = re.fullmatch(r"(\d{3})\.yaml", path.name)
        if m:
            nums.append(int(m.group(1)))
    return sorted(nums)
