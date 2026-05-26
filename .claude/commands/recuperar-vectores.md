# Skill: Recuperar Vectores y HTML

Recupera archivos de diseno vectorial SVG, EPS, AI y archivos HTML borrados.

## Pasos

1. Verificar Python: `python --version`
2. Preguntar disco destino (letra diferente a C:)
3. Si el usuario quiere carpeta personalizada, editar `OUTPUT` en `scripts/recuperar_vectores_html.py`
4. Decirle que abra CMD como Administrador y ejecute:

```
python scripts/recuperar_vectores_html.py
```

5. El script busca etiquetas de texto como `<svg`, `%!PS-Adobe`, `<!DOCTYPE html`
6. Los SVG se pueden abrir directamente en el navegador para verificarlos
7. Los EPS y AI requieren Adobe Illustrator o Inkscape (gratis) para abrirlos
8. Los HTML recuperados pueden tener recursos externos faltantes (imagenes, CSS) pero el contenido de texto estara intacto

## Nota

Los archivos de texto como SVG y HTML son mas fragiles en la recuperacion porque cualquier byte dañado puede hacer el archivo invalido. Si un SVG no abre, intentar con Inkscape que es mas tolerante a errores.
