import os
import sys

_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _dir)
try:
    from config import DISCO, OUTPUT_VECTORES as OUTPUT
except ImportError:
    DISCO  = r'\\.\C:'
    OUTPUT = r'D:\omnibook 2026 nano\Vectores_HTML_recuperados'

CHUNK   = 4 * 1024 * 1024      # 4MB por lectura
MAX_TAM = 100 * 1024 * 1024    # 100MB maximo
MIN_TAM = 500                  # minimo 500 bytes
OUTPUT  = r'D:\omnibook 2026 nano\Vectores_HTML_recuperados'

# Firmas con sus marcadores de fin y extension
FORMATOS = [
    # Vectores
    (b'<svg',        b'</svg>',       '.svg'),
    (b'<SVG',        b'</SVG>',       '.svg'),
    (b'<?xml',       b'</svg>',       '.svg'),   # SVG con cabecera XML
    (b'%!PS-Adobe',  b'%%EOF',        '.eps'),   # EPS / PostScript
    (b'%AI',         b'%%EOF',        '.ai'),    # Adobe Illustrator
    # HTML / Web
    (b'<!DOCTYPE html', b'</html>',   '.html'),
    (b'<!DOCTYPE HTML', b'</HTML>',   '.html'),
    (b'<html',       b'</html>',      '.html'),
    (b'<HTML',       b'</HTML>',      '.html'),
]

def buscar_sig(buf, desde=0):
    mejor_pos = -1
    mejor_ini = b''
    mejor_fin = b''
    mejor_ext = ''

    for ini, fin, ext in FORMATOS:
        pos = buf.find(ini, desde)
        if pos != -1 and (mejor_pos == -1 or pos < mejor_pos):
            mejor_pos = pos
            mejor_ini = ini
            mejor_fin = fin
            mejor_ext = ext

    return mejor_pos, mejor_ini, mejor_fin, mejor_ext

def recover():
    os.makedirs(OUTPUT, exist_ok=True)
    count  = 0
    buf    = b''
    leidos = 0
    ticker = 0
    totales = {'svg': 0, 'eps': 0, 'ai': 0, 'html': 0}

    print("=" * 50)
    print("  RECUPERADOR DE VECTORES Y HTML")
    print("  Formatos: SVG, EPS, AI, HTML")
    print(f"  Guardando en: {OUTPUT}")
    print("=" * 50)

    try:
        with open(r'\\.\C:', 'rb') as disco:
            while True:
                chunk = disco.read(CHUNK)
                if not chunk:
                    break

                buf    += chunk
                leidos += len(chunk)
                ticker += 1

                while True:
                    pos, ini, fin, ext = buscar_sig(buf)
                    if pos == -1:
                        buf = buf[-32:]
                        break

                    fin_pos = buf.find(fin, pos + len(ini))

                    if fin_pos == -1:
                        if len(buf) - pos > MAX_TAM:
                            buf = buf[pos + len(ini):]
                            continue
                        buf = buf[pos:]
                        break

                    fin_pos += len(fin)
                    datos = buf[pos:fin_pos]

                    if len(datos) >= MIN_TAM:
                        tipo = ext.replace('.', '')
                        nombre = os.path.join(OUTPUT, f'{tipo}_{count:04d}{ext}')
                        with open(nombre, 'wb') as f:
                            f.write(datos)
                        count += 1
                        totales[tipo] = totales.get(tipo, 0) + 1
                        kb = len(datos) // 1024
                        print(f"  [+] {tipo}_{count:04d}{ext}  ({kb} KB)")

                    buf = buf[fin_pos:]

                if ticker % 250 == 0:
                    print(f"  ... {leidos / (1024**3):.1f} GB | SVG:{totales.get('svg',0)} EPS:{totales.get('eps',0)} AI:{totales.get('ai',0)} HTML:{totales.get('html',0)}")

    except PermissionError:
        print("\n  ERROR: Abre el CMD como Administrador e intenta de nuevo.")
        sys.exit(1)
    except Exception as e:
        print(f"\n  Error: {e}")

    print("\n" + "=" * 50)
    print(f"  Listo! {count} archivos guardados en:")
    print(f"  {OUTPUT}")
    print(f"  SVG:{totales.get('svg',0)} | EPS:{totales.get('eps',0)} | AI:{totales.get('ai',0)} | HTML:{totales.get('html',0)}")
    print("=" * 50)

if __name__ == '__main__':
    recover()
