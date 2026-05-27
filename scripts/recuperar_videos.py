import os
import sys
import struct

_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _dir)
try:
    from config import DISCO, OUTPUT_VIDEOS as OUTPUT
except ImportError:
    DISCO  = r'\\.\C:'
    OUTPUT = r'D:\omnibook 2026 nano\Videos_recuperados'

CHUNK     = 4 * 1024 * 1024    # 4MB por lectura
MAX_VIDEO = 4 * 1024 * 1024 * 1024  # 4GB maximo por video
MIN_VIDEO = 100 * 1024              # minimo 100KB para ignorar fragmentos
OUTPUT    = r'D:\omnibook 2026 nano\Videos_recuperados'

# Firmas de video: (patron, bytes_antes_del_patron, extension)
SIGS = [
    (b'ftyp', 4, '.mp4'),           # MP4 / MOV
    (b'\x1a\x45\xdf\xa3', 0, '.mkv'),  # MKV / WEBM
]

def buscar_sig(buf, desde=0):
    mejor_pos = -1
    mejor_ext = ''
    mejor_pre = 0

    for sig, pre, ext in SIGS:
        pos = buf.find(sig, desde)
        if pos == -1:
            continue
        pos_real = pos - pre
        if pos_real < 0:
            continue
        if mejor_pos == -1 or pos_real < mejor_pos:
            mejor_pos = pos_real
            mejor_ext = ext
            mejor_pre = pre

    return mejor_pos, mejor_ext

def recover():
    os.makedirs(OUTPUT, exist_ok=True)
    count  = 0
    buf    = b''
    leidos = 0
    ticker = 0

    print("=" * 50)
    print("  RECUPERADOR DE VIDEOS - Escaneando disco C:")
    print("  Formatos: MP4, MOV, MKV, WEBM")
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
                    pos, ext = buscar_sig(buf)
                    if pos == -1:
                        buf = buf[-8:]
                        break

                    siguiente, _ = buscar_sig(buf, pos + MIN_VIDEO)

                    if siguiente == -1:
                        if len(buf) - pos > MAX_VIDEO:
                            buf = buf[pos + 4:]
                            continue
                        buf = buf[pos:]
                        break

                    datos = buf[pos:siguiente]

                    if len(datos) >= MIN_VIDEO:
                        nombre = os.path.join(OUTPUT, f'video_{count:04d}{ext}')
                        with open(nombre, 'wb') as f:
                            f.write(datos)
                        count += 1
                        mb = len(datos) // (1024 * 1024)
                        print(f"  [+] video_{count:04d}{ext}  ({mb} MB)")

                    buf = buf[siguiente:]

                if ticker % 250 == 0:
                    print(f"  ... {leidos / (1024**3):.1f} GB escaneados | {count} videos recuperados")

    except PermissionError:
        print("\n  ERROR: Abre el CMD como Administrador e intenta de nuevo.")
        sys.exit(1)
    except Exception as e:
        print(f"\n  Error: {e}")

    print("\n" + "=" * 50)
    print(f"  Listo! {count} videos guardados en:")
    print(f"  {OUTPUT}")
    print("=" * 50)

if __name__ == '__main__':
    recover()
