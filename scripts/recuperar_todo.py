import os
import sys
import subprocess
import time

SCRIPTS = [
    ('recuperar_png.py',             'Imagenes PNG'),
    ('recuperar_jpg.py',             'Fotos JPG'),
    ('recuperar_videos.py',          'Videos MP4/MOV/MKV'),
    ('recuperar_docs.py',            'Documentos PDF/Word'),
    ('recuperar_mp3.py',             'Musica MP3/OGG/FLAC'),
    ('recuperar_vectores_html.py',   'Vectores SVG/EPS/AI y HTML'),
    ('recuperar_excel.py',           'Excel y PowerPoint'),
    ('recuperar_raw.py',             'Fotos RAW de camara'),
    ('recuperar_zip.py',             'Archivos ZIP y RAR'),
    ('recuperar_carpetas_v2.py',     'Carpetas con estructura original (MFT + validacion)'),
]

DIR = os.path.dirname(os.path.abspath(__file__))

def banner():
    print("=" * 60)
    print("   RECUPERADOR MAESTRO DE ARCHIVOS")
    print("   Recupera PNG, JPG, Videos, Docs, Musica y Vectores")
    print("=" * 60)
    print()

def confirmar():
    print("  Este proceso puede tardar varias horas dependiendo")
    print("  del tamano del disco. No cierres esta ventana.")
    print()
    r = input("  Continuar? (s/n): ").strip().lower()
    if r != 's':
        print("  Cancelado.")
        sys.exit(0)
    print()

def correr_script(nombre, descripcion, numero, total):
    ruta = os.path.join(DIR, nombre)
    print()
    print("=" * 60)
    print(f"  [{numero}/{total}] {descripcion}")
    print(f"  Script: {nombre}")
    print("=" * 60)

    inicio = time.time()

    try:
        resultado = subprocess.run(
            [sys.executable, ruta],
            check=False
        )
        duracion = (time.time() - inicio) / 60
        if resultado.returncode == 0:
            print(f"\n  Completado en {duracion:.1f} minutos.")
        else:
            print(f"\n  Termino con errores (codigo {resultado.returncode}).")
    except Exception as e:
        print(f"\n  Error al correr {nombre}: {e}")

def resumen(resultados):
    print()
    print("=" * 60)
    print("  RESUMEN FINAL")
    print("=" * 60)
    for nombre, descripcion, estado in resultados:
        icono = "OK" if estado == 'ok' else "ERROR"
        print(f"  [{icono}] {descripcion}")
    print()
    print("  Revisa las carpetas de destino en tu disco D:")
    print("  para ver todos los archivos recuperados.")
    print("=" * 60)

def main():
    banner()

    try:
        confirmar()
    except KeyboardInterrupt:
        print("\n  Cancelado.")
        sys.exit(0)

    total = len(SCRIPTS)
    resultados = []

    for i, (nombre, descripcion) in enumerate(SCRIPTS, 1):
        try:
            correr_script(nombre, descripcion, i, total)
            resultados.append((nombre, descripcion, 'ok'))
        except KeyboardInterrupt:
            print(f"\n  Script {nombre} interrumpido por el usuario.")
            continuar = input("  Continuar con el siguiente? (s/n): ").strip().lower()
            resultados.append((nombre, descripcion, 'interrumpido'))
            if continuar != 's':
                break

    resumen(resultados)

if __name__ == '__main__':
    main()
