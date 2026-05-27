import os
import sys

_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _dir)
try:
    from config import DISCO, OUTPUT_ZIP as OUTPUT
except ImportError:
    DISCO  = r'\\.\C:'
    OUTPUT = r'D:\omnibook 2026 nano\Comprimidos_recuperados'

CHUNK   = 4 * 1024 * 1024
MAX_ZIP = 4 * 1024 * 1024 * 1024
MIN_ZIP = 1 * 1024

SIGS = [
    (b'PK\x03\x04',           b'PK\x05\x06', '.zip', 'ZIP'),
    (b'Rar!\x1a\x07\x00',     None,           '.rar', 'RAR v4'),
    (b'Rar!\x1a\x07\x01\x00', None,           '.rar', 'RAR v5'),
    (b'7z\xbc\xaf\x27\x1c',   None,           '.7z',  '7-ZIP'),
    (b'\x1f\x8b\x08',         None,           '.gz',  'GZIP'),
]


def buscar_sig(buf, desde=0):
    mejor_pos = -1
    mejor_sig = b''
    mejor_fin = None
    mejor_ext = ''
    mejor_desc = ''

    for sig, fin, ext, desc in SIGS:
        pos = buf.find(sig, desde)
        if pos != -1 and (mejor_pos == -1 or pos < mejor_pos):
            mejor_pos  = pos
            mejor_sig  = sig
            mejor_fin  = fin
            mejor_ext  = ext
            mejor_desc = desc

    return mejor_pos, mejor_sig, mejor_fin, mejor_ext, mejor_desc


def recover():
    os.makedirs(OUTPUT, exist_ok=True)
    count  = 0
    buf    = b''
    leidos = 0
    ticker = 0
    totales = {}

    print("=" * 55)
    print("  RECUPERADOR DE COMPRIMIDOS")
    print("  Formatos: ZIP, RAR, 7Z, GZ")
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
                    pos, sig, fin_sig, ext, desc = buscar_sig(buf)
                    if pos == -1:
                        buf = buf[-16:]
                        break

                    if fin_sig:
                        fin_pos = buf.find(fin_sig, pos + len(sig))
                        if fin_pos == -1:
                            if len(buf) - pos > MAX_ZIP:
                                buf = buf[pos + len(sig):]
                                continue
                            buf = buf[pos:]
                            break
                        fin_pos += len(fin_sig) + 18  # EOCD tiene 22 bytes, ya tenemos 4
                        datos = buf[pos:fin_pos]
                    else:
                        siguiente, _, _, _, _ = buscar_sig(buf, pos + MIN_ZIP)
                        if siguiente == -1:
                            if len(buf) - pos > MAX_ZIP:
                                buf = buf[pos + len(sig):]
                                continue
                            buf = buf[pos:]
                            break
                        datos = buf[pos:siguiente]

                    if len(datos) >= MIN_ZIP:
                        nombre = os.path.join(OUTPUT, f'archivo_{count:04d}{ext}')
                        with open(nombre, 'wb') as f:
                            f.write(datos)
                        count += 1
                        totales[ext] = totales.get(ext, 0) + 1
                        kb = len(datos) // 1024
                        print(f"  [+] archivo_{count:04d}{ext}  ({kb} KB)  {desc}")

                    buf = buf[fin_pos if fin_sig else siguiente:]

                if ticker % 250 == 0:
                    print(f"  ... {leidos/(1024**3):.1f} GB | {count} archivos")

    except PermissionError:
        print("\n  ERROR: Abre CMD como Administrador.")
        sys.exit(1)
    except Exception as e:
        print(f"\n  Error: {e}")

    print("\n" + "=" * 55)
    print(f"  Listo! {count} archivos comprimidos guardados en:")
    print(f"  {OUTPUT}")
    for ext, n in totales.items():
        print(f"    {ext}: {n}")
    print("=" * 55)


if __name__ == '__main__':
    recover()
