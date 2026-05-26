# Skill: Recuperar Todo

Corre todos los scripts de recuperacion en secuencia: PNG, JPG, Videos, Documentos, Musica y Vectores/HTML.

## Pasos

1. Verificar Python: `python --version`
2. Advertir al usuario que el proceso puede tardar varias horas
3. Verificar que el disco destino tenga suficiente espacio libre (recomendado minimo 50GB)
4. Preguntar si quiere cambiar la carpeta destino en cada script antes de empezar
5. Decirle que abra CMD como Administrador y ejecute:

```
python scripts/recuperar_todo.py
```

6. Explicar que el script preguntara si desea continuar antes de arrancar
7. Explicar el orden de ejecucion:
   - [1/6] Imagenes PNG
   - [2/6] Fotos JPG
   - [3/6] Videos MP4/MOV/MKV
   - [4/6] Documentos PDF/Word
   - [5/6] Musica MP3/OGG/FLAC
   - [6/6] Vectores SVG/EPS/AI y HTML

8. Si el usuario interrumpe un script con Ctrl+C, el maestro pregunta si continuar con el siguiente
9. Al final muestra un resumen con cuales completaron y cuales fallaron

## Advertencias importantes

- NO instalar programas ni descargar archivos mientras corre — cada escritura puede sobreescribir datos recuperables
- Guardar SIEMPRE en un disco diferente al C:
- No apagar ni reiniciar la PC durante el proceso
- Si el disco destino se llena, parar y liberar espacio antes de continuar

## Cuando termina

Revisar estas carpetas en el disco destino:
- `PNGs_recuperados/`
- `JPGs_recuperados/`
- `Videos_recuperados/`
- `Documentos_recuperados/`
- `Musica_recuperada/`
- `Vectores_HTML_recuperados/`

Abrir cada carpeta en vista de iconos grandes para identificar visualmente los archivos recuperados.
