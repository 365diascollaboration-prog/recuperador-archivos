import os
import sys

_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _dir)
try:
    from config import DISCO, OUTPUT_EXCEL as OUTPUT
except ImportError:
    DISCO  = r'\\.\C:'
    OUTPUT = r'D:\omnibook 2026 nano\Excel_PowerPoint_recuperados'

CHUNK   = 4 * 1024 * 1024
MAX_TAM = 500 * 1024 * 1024
MIN_TAM = 5 * 1024

# ZIP moderno (xlsx, xlsb, pptx) + XLS/PPT legacy (OLE2)
FORMATOS = [
    (b'PK\x03\x04',         b'xl/',          '.xlsx',  'Excel moderno'),
    (b'PK\x03\x04',         b'ppt/',         '.pptx',  'PowerPoint moderno'),
    (b'PK\x03\x04',         b'word/',        '.docx',  'Word moderno'),
    (b'\xd0\xcf\x11\xe0',   b'\x00',         '.xls',   'Excel antiguo'),
]

OLE2_SIG = b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'
ZIP_SIG  = b'PK\x03\x04'


def es_excel_zip(buf, pos):
    fragmento = buf[pos:pos+2048]
    return b'xl/' in fragmento or b'[Content_Types]' in fragmento


def es_pptx_zip(buf, pos):
    fragmento = buf[pos:pos+2048]
    return b'ppt/' in fragmento


def buscar_sig(buf, desde=0):
    mejor_pos = -1
    mejor_ext = ''
    mejor_desc = ''

    # OLE2 (xls, ppt antiguos)
    p = buf.find(OLE2_SIG, desde)
    if p != -1 and (mejor_pos == -1 or p < mejor_pos):
        mejor_pos = p
        mejor_ext = '.xls'
        mejor_desc = 'Office antiguo (XLS/PPT/DOC)'

    # ZIP moderno
    p = desde
    while True:
        p = buf.find(ZIP_SIG, p)
        if p == -1:
            break
        if es_excel_zip(buf, p):
            if mejor_pos == -1 or p < mejor_pos:
                mejor_pos = p
                mejor_ext = '.xlsx'
                mejor_desc = 'Excel (.xlsx)'
            break
        elif es_pptx_zip(buf, p):
            if mejor_pos == -1 or p < mejor_pos:
                mejor_pos = p
                mejor_ext = '.pptx'
                mejor_desc = 'PowerPoint (.pptx)'
            break
        p += 4

    return mejor_pos, mejor_ext, mejor_desc


def recover():
    os.makedirs(OUTPUT, exist_ok=True)
    count  = 0
    buf    = b''
    leidos = 0
    ticker = 0
    totales = {}

    print("=" * 55)
    print("  RECUPERADOR DE EXCEL Y POWERPOINT")
    print("  Formatos: .xlsx .xls .pptx .ppt")
    print(f"  Guardando en: {OUTPUT}")
    print("=" * 55)

    try:
        with open(DISCO, 'rb') as disco:
            while True:
                chunk = disco.read(CHUNK)
                if not chunk:
                    break
                buf    += chunk
                leidos += len(chunk)
                ticker += 1

                while True:
                    pos, ext, desc = buscar_sig(buf)
                    if pos == -1:
                        buf = buf[-16:]
                        break

                    siguiente, _, _ = buscar_sig(buf, pos + MIN_TAM)
                    if siguiente == -1:
                        if len(buf) - pos > MAX_TAM:
                            buf = buf[pos + 4:]
                            continue
                        buf = buf[pos:]
                        break

                    datos = buf[pos:siguiente]
                    if len(datos) >= MIN_TAM:
                        nombre = os.path.join(OUTPUT, f'archivo_{count:04d}{ext}')
                        with open(nombre, 'wb') as f:
                            f.write(datos)
                        count += 1
                        totales[ext] = totales.get(ext, 0) + 1
                        print(f"  [+] archivo_{count:04d}{ext}  ({len(datos)//1024} KB)  {desc}")

                    buf = buf[siguiente:]

                if ticker % 250 == 0:
                    print(f"  ... {leidos/(1024**3):.1f} GB | {count} archivos")

    except PermissionError:
        print("\n  ERROR: Abre CMD como Administrador.")
        sys.exit(1)
    except Exception as e:
        print(f"\n  Error: {e}")

    print("\n" + "=" * 55)
    print(f"  Listo! {count} archivos guardados en:")
    print(f"  {OUTPUT}")
    for ext, n in totales.items():
        print(f"    {ext}: {n}")
    print("=" * 55)


if __name__ == '__main__':
    recover()
