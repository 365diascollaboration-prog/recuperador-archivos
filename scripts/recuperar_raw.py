import os
import sys

_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _dir)
try:
    from config import DISCO, OUTPUT_RAW as OUTPUT
except ImportError:
    DISCO  = r'\\.\C:'
    OUTPUT = r'D:\omnibook 2026 nano\Fotos_RAW_recuperadas'

CHUNK   = 4 * 1024 * 1024
MAX_RAW = 100 * 1024 * 1024
MIN_RAW = 500 * 1024   # minimo 500KB — RAW siempre son grandes

# Firmas RAW por marca de camara
SIGS = [
    (b'II\x2a\x00',  '.cr2',  'Canon RAW (CR2)'),       # Canon CR2 / TIFF LE
    (b'II\x2a\x00',  '.nef',  'Nikon RAW (NEF)'),        # Nikon NEF / TIFF LE
    (b'MM\x00\x2a',  '.tiff', 'TIFF Big Endian'),        # TIFF BE / ARW Sony
    (b'II\x55\x00',  '.rw2',  'Panasonic RAW (RW2)'),
    (b'FUJIFILMCCD-RAW', '.raf', 'Fujifilm RAW (RAF)'),
    (b'IIU\x00',     '.dng',  'Adobe DNG'),
    (b'\x00\x00\x00\x0cjP  ', '.heic', 'HEIC / HEIF'),   # iPhone moderno
    (b'\xff\xd8\xff', '.jpg', 'JPEG (camara)'),
]


def buscar_sig(buf, desde=0):
    mejor_pos = -1
    mejor_ext = ''
    mejor_desc = ''

    for sig, ext, desc in SIGS:
        pos = buf.find(sig, desde)
        if pos != -1 and (mejor_pos == -1 or pos < mejor_pos):
            mejor_pos = pos
            mejor_ext = ext
            mejor_desc = desc

    return mejor_pos, mejor_ext, mejor_desc


def recover():
    os.makedirs(OUTPUT, exist_ok=True)
    count  = 0
    buf    = b''
    leidos = 0
    ticker = 0
    totales = {}

    print("=" * 55)
    print("  RECUPERADOR DE FOTOS RAW")
    print("  Canon CR2, Nikon NEF, Sony ARW, DNG, HEIC...")
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
                        buf = buf[-32:]
                        break

                    siguiente, _, _ = buscar_sig(buf, pos + MIN_RAW)
                    if siguiente == -1:
                        if len(buf) - pos > MAX_RAW:
                            buf = buf[pos + len(SIGS[0][0]):]
                            continue
                        buf = buf[pos:]
                        break

                    datos = buf[pos:siguiente]
                    if len(datos) >= MIN_RAW:
                        nombre = os.path.join(OUTPUT, f'raw_{count:04d}{ext}')
                        with open(nombre, 'wb') as f:
                            f.write(datos)
                        count += 1
                        totales[ext] = totales.get(ext, 0) + 1
                        mb = len(datos) // (1024 * 1024)
                        print(f"  [+] raw_{count:04d}{ext}  ({mb} MB)  {desc}")

                    buf = buf[siguiente:]

                if ticker % 250 == 0:
                    print(f"  ... {leidos/(1024**3):.1f} GB | {count} fotos RAW")

    except PermissionError:
        print("\n  ERROR: Abre CMD como Administrador.")
        sys.exit(1)
    except Exception as e:
        print(f"\n  Error: {e}")

    print("\n" + "=" * 55)
    print(f"  Listo! {count} fotos RAW guardadas en:")
    print(f"  {OUTPUT}")
    for ext, n in totales.items():
        print(f"    {ext}: {n}")
    print("=" * 55)


if __name__ == '__main__':
    recover()
