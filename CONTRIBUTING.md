# Como Contribuir

Gracias por querer mejorar este proyecto. Aqui esta todo lo que necesitas saber.

## Formas de contribuir

- **Agregar soporte para nuevos formatos** — agrega la firma binaria en el script correspondiente
- **Mejorar la deteccion** — algunos formatos tienen firmas ambiguas, mejora la logica de validacion
- **Reportar bugs** — abre un Issue describiendo el problema y en que sistema ocurrio
- **Mejorar documentacion** — corrige errores, agrega ejemplos, traduce a otros idiomas
- **Agregar interfaz grafica** — el proyecto acepta PR con GUI en tkinter u otro framework

## Como agregar un nuevo formato

1. Encuentra la firma binaria (magic bytes) del formato en [Gary Kessler's File Signatures](https://www.garykessler.net/library/file_sigs.html)
2. Agrega la firma al script correspondiente o crea uno nuevo siguiendo la estructura existente
3. Usa `config.py` para la ruta de salida
4. Prueba que recupera archivos reales antes de hacer PR

## Estructura del proyecto

```
recuperador-archivos/
├── scripts/
│   ├── config.py              ← configuracion central (disco y rutas)
│   ├── recuperar_todo.py      ← script maestro
│   ├── recuperar_png.py
│   ├── recuperar_jpg.py
│   ├── recuperar_videos.py
│   ├── recuperar_docs.py
│   ├── recuperar_mp3.py
│   ├── recuperar_vectores_html.py
│   ├── recuperar_excel.py
│   ├── recuperar_raw.py
│   ├── recuperar_zip.py
│   ├── recuperar_carpetas.py
│   └── recuperar_carpetas_v2.py
├── .claude/commands/          ← skills para Claude Code AI
├── docs/                      ← documentacion tecnica
├── assets/                    ← capturas de pantalla
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
└── LICENSE
```

## Proceso para hacer un PR

1. Fork del repositorio
2. Crea una rama: `git checkout -b agregar-formato-xyz`
3. Haz tus cambios
4. Prueba que funciona con CMD como Administrador
5. Commit con mensaje descriptivo
6. Abre el PR describiendo que formato agregaste y como lo probaste

## Estandar de codigo

- Python puro — sin dependencias externas
- Cada script debe funcionar de forma independiente
- Importar config.py con fallback si no existe
- Mostrar progreso en pantalla cada ~1GB escaneado
- Mensaje claro de error si no se ejecuta como Administrador
