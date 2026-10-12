#!/usr/bin/env python3
"""Genera, desde cv.yaml, el .tex del CV (build/cv.tex) y el sitio web (dist/)."""
import datetime
import math
import re
import shutil
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup, escape

ROOT = Path(__file__).parent
BUILD = ROOT / "build"
DIST = ROOT / "dist"

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


# ---------- filtros ----------
TEX_ESCAPES = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
    "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def tex(value):
    s = "".join(TEX_ESCAPES.get(c, c) for c in str(value).strip())
    s = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", s)
    for old, new in (("“", "``"), ("”", "''"), ("’", "'"), ("–", "--"),
                     ("—", "---"), ("→", r"$\rightarrow$")):
        s = s.replace(old, new)
    return s


def md(value):
    """Escapa HTML y convierte **negritas**."""
    return Markup(re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", str(escape(value))))


def es(value):
    """Devuelve el texto en español si el valor es {en, es}; si no, el mismo valor."""
    return value.get("es", value.get("en")) if isinstance(value, dict) else value


# ---------- ilustración del hero ----------
def hero_svg():
    """Esfera de cristal con ondas apiladas, generada con código (sin imágenes)."""
    waves = []
    n = 15
    for i in range(n):
        y = 212 + i * 11
        amp = 7 + (i % 4) * 2
        sign = 1 if i % 2 == 0 else -1
        d = f"M -80 {y}"
        x = -80
        k = 0
        while x < 480:
            peak = y - sign * amp * (1 if k % 2 == 0 else -1)
            d += f" Q {x + 35} {peak} {x + 70} {y}"
            x += 70
            k += 1
        d += f" L 480 460 L -80 460 Z"
        delay = -(i * 0.9)
        waves.append(
            f'<path class="onda" style="animation-delay:{delay:.1f}s" d="{d}"/>'
        )
    return Markup(f"""
<svg class="esfera" viewBox="0 0 400 400" role="presentation" focusable="false">
  <defs>
    <radialGradient id="cuerpo" cx="34%" cy="26%" r="85%">
      <stop offset="0" stop-color="#8af0f7"/>
      <stop offset=".28" stop-color="#4f6bff"/>
      <stop offset=".62" stop-color="#7a22d8"/>
      <stop offset="1" stop-color="#d12cf0"/>
    </radialGradient>
    <linearGradient id="trazo" x1="0" x2="1">
      <stop offset="0" stop-color="#d12cf0"/>
      <stop offset=".55" stop-color="#7a6bff"/>
      <stop offset="1" stop-color="#3ad4e6"/>
    </linearGradient>
    <linearGradient id="relleno" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#241060"/>
      <stop offset="1" stop-color="#0c0a2e"/>
    </linearGradient>
    <clipPath id="recorte"><circle cx="200" cy="200" r="150"/></clipPath>
    <filter id="brillo" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="6"/>
    </filter>
  </defs>
  <circle cx="200" cy="200" r="150" fill="url(#cuerpo)"/>
  <g clip-path="url(#recorte)">{''.join(waves)}</g>
  <ellipse cx="150" cy="112" rx="62" ry="26" transform="rotate(-28 150 112)"
           fill="#fff" opacity=".38" filter="url(#brillo)"/>
  <ellipse cx="258" cy="96" rx="14" ry="7" transform="rotate(-28 258 96)"
           fill="#fff" opacity=".55" filter="url(#brillo)"/>
  <circle cx="200" cy="200" r="150" fill="none" stroke="url(#trazo)" stroke-width="2" opacity=".9"/>
</svg>""")


def logo_svg():
    dots = []
    for i in range(48):
        a = i / 48 * 2 * math.pi
        r = 21
        dots.append(f'<circle cx="{25 + r * math.cos(a):.2f}" cy="{25 + r * math.sin(a):.2f}" r="1.1"/>')
    return Markup(
        '<svg class="logo" viewBox="0 0 50 50" role="presentation" focusable="false">'
        f'<g fill="#d12cf0">{"".join(dots)}</g>'
        '<text x="25" y="23" text-anchor="middle" font-size="10" fill="#fff">E</text>'
        '<text x="25" y="35" text-anchor="middle" font-size="10" fill="#fff">M</text></svg>'
    )


# ---------- construcción ----------
def load_data():
    with open(ROOT / "cv.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_tex(data):
    env = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        block_start_string=r"\BLOCK{", block_end_string="}",
        variable_start_string=r"\VAR{", variable_end_string="}",
        comment_start_string=r"\#{", comment_end_string="}",
        trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True,
        autoescape=False,
    )
    env.filters["tex"] = tex
    out = env.get_template("cv.tex.j2").render(**data)
    BUILD.mkdir(exist_ok=True)
    (BUILD / "cv.tex").write_text(out, encoding="utf-8")


def build_site(data):
    env = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=select_autoescape(["html", "j2"]),
    )
    env.filters["md"] = md
    env.filters["es"] = es
    today = datetime.date.today()
    built = f"{today.day} de {MESES[today.month - 1]} de {today.year}"
    html = env.get_template("index.html.j2").render(
        d=data, built=built, year=today.year,
        hero=hero_svg(), logo=logo_svg(),
    )
    DIST.mkdir(exist_ok=True)
    (DIST / "index.html").write_text(html, encoding="utf-8")
    for asset in (ROOT / "site").iterdir():
        shutil.copy(asset, DIST / asset.name)
    (DIST / ".nojekyll").write_text("", encoding="utf-8")


def main():
    data = load_data()
    build_tex(data)
    build_site(data)
    print("OK -> build/cv.tex, dist/index.html")


if __name__ == "__main__":
    main()
