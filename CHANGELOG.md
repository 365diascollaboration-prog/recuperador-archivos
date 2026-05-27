# Changelog

## v1.3.0 — 2026-05-26

### Agregado
- `recuperar_excel.py` — recupera Excel (.xlsx, .xls) y PowerPoint (.pptx, .ppt)
- `recuperar_raw.py` — recupera fotos RAW de camara (Canon CR2, Nikon NEF, Sony ARW, DNG, HEIC)
- `recuperar_zip.py` — recupera archivos comprimidos (ZIP, RAR, 7Z, GZ)
- `config.py` — configuracion central: cambia disco y ruta de salida en un solo lugar
- `CONTRIBUTING.md` — guia para contribuir al proyecto
- `docs/archivos-encriptados-chrome.md` — explica los archivos .tmp GUID de Chrome y DPAPI
- Skills de Claude Code para carpetas v1 y v2

### Mejorado
- `recuperar_carpetas_v2.py` — combina lectura MFT con validacion de firmas binarias
- `recuperar_todo.py` — ahora incluye todos los scripts incluyendo los nuevos y carpetas v2
- Todos los scripts ahora importan desde `config.py` con fallback automatico
- README actualizado con seccion de documentacion y tabla de tipos de archivos

---

## v1.2.0 — 2026-05-26

### Agregado
- `recuperar_carpetas.py` — recupera archivos con estructura de carpetas original leyendo MFT de NTFS
- `recuperar_carpetas_v2.py` — version mejorada con validacion de firmas para evitar guardar basura
- Capturas de pantalla reales en el README
- Skills de Claude Code AI para todos los tipos de archivo

---

## v1.1.0 — 2026-05-26

### Agregado
- `recuperar_todo.py` — script maestro que corre todos los scripts en secuencia
- Skills de Claude Code (`.claude/commands/`) para guiar el proceso con AI
- README mejorado con badges, historia real y capturas de pantalla

---

## v1.0.0 — 2026-05-26

### Lanzamiento inicial
- `recuperar_png.py` — recupera imagenes PNG por firma binaria
- `recuperar_jpg.py` — recupera fotos JPG
- `recuperar_videos.py` — recupera videos MP4, MOV, MKV, WEBM
- `recuperar_docs.py` — recupera documentos PDF, Word .doc y .docx
- `recuperar_mp3.py` — recupera musica MP3, OGG, FLAC
- `recuperar_vectores_html.py` — recupera vectores SVG, EPS, AI y HTML
- README con instrucciones completas
- Licencia MIT
