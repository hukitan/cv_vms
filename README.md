# Portafolio y CV desde un solo archivo

Edita **`cv.yaml`**. Con cada push, GitHub Actions genera:

- el PDF del CV (`Elias_Mina_CV_Data_Analyst.pdf`, publicado en el release `CV`),
- la página web (GitHub Pages).

## Estructura
- `cv.yaml`: todo el contenido (experiencia, proyectos, habilidades, contacto).
- `templates/cv.tex.j2`: diseño LaTeX del CV.
- `templates/index.html.j2`, `site/style.css`, `site/app.js`: diseño de la web.
- `build.py`: lee `cv.yaml` y genera `build/cv.tex` y `dist/`.

## Uso local
```bash
pip install -r requirements.txt
python build.py          # genera build/cv.tex y dist/index.html
```
Abre `dist/index.html` en el navegador.

## Configuración única en GitHub
Settings → Pages → Source: **GitHub Actions**.

## Cambios frecuentes
- Nuevo proyecto: agrega un bloque en `projects:` de `cv.yaml`.
- Nuevo año o puesto: edita `experience:`; el nombre del PDF no cambia.
- Texto del CV en inglés y de la web en español: cada texto con `{en, es}` se usa donde corresponde.
# cv_vms
