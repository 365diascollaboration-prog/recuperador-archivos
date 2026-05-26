# Recuperador de Archivos

Herramientas gratuitas y de codigo abierto para recuperar archivos borrados del disco duro usando Python. Recupera fotos, videos, musica, documentos, vectores y mas directamente desde los sectores del disco.

## Como funciona

Cada script escanea el disco sector por sector buscando la firma binaria de cada tipo de archivo. Los archivos borrados siguen en el disco hasta que son sobreescritos, por eso es posible recuperarlos.

## Requisitos

- Windows 10 / 11
- Python 3.x instalado
- CMD abierto como **Administrador**

## Scripts disponibles

| Script | Recupera |
|--------|----------|
| `recuperar_png.py` | Imagenes PNG |
| `recuperar_jpg.py` | Fotos JPG |
| `recuperar_videos.py` | Videos MP4, MOV, MKV, WEBM |
| `recuperar_docs.py` | Documentos PDF, Word .doc, .docx |
| `recuperar_mp3.py` | Musica MP3, OGG, FLAC |
| `recuperar_vectores_html.py` | Vectores SVG, EPS, AI y archivos HTML |

## Uso

1. Abre CMD como **Administrador**
2. Ejecuta el script que necesitas:

```bash
python scripts/recuperar_png.py
python scripts/recuperar_jpg.py
python scripts/recuperar_videos.py
python scripts/recuperar_docs.py
python scripts/recuperar_mp3.py
python scripts/recuperar_vectores_html.py
```

3. Los archivos recuperados se guardan en `D:\omnibook 2026 nano\` por defecto. Puedes cambiar la variable `OUTPUT` dentro de cada script.

## Consejos importantes

- **No instales nada ni descargues archivos** mientras corres el script — cada escritura puede sobreescribir los datos que quieres recuperar
- Guarda los archivos recuperados en un **disco diferente** al que estes escaneando
- Mientras mas reciente sea el borrado, mas probabilidad de recuperar los archivos

## Personalizar la carpeta de destino

Abre el script y cambia la linea `OUTPUT`:

```python
OUTPUT = r'D:\mi_carpeta\recuperados'
```

## Licencia

MIT License — libre para usar, modificar y distribuir.

## Contribuir

Pull requests bienvenidos. Si quieres agregar soporte para otros formatos, abre un issue o manda tu PR.
