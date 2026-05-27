import os
import sys

_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _dir)
try:
    from config import DISCO, OUTPUT_JPG as OUTPUT
except ImportError:
    DISCO  = r'\\.\C:'
    OUTPUT = r'D:\omnibook 2026 nano\JPGs_recuperados'

JPG_SIG  = b'\xff\xd8\xff'
JPG_END  = b'\xff\xd9'
CHUNK    = 4 * 1024 * 1024   # 4MB por lectura
MAX_JPG  = 50 * 1024 * 1024  # maximo 50MB por foto
OUTPUT   = r'D:\omnibook 2026 nano\JPGs_recuperados'

def recover():
    os.makedirs(OUTPUT, exist_ok=True)
    count  = 0
    buf    = b''
    leidos = 0
    ticker = 0

    print("=" * 50)
    print("  RECUPERADOR DE FOTOS JPG - Escaneando disco C:")
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
                    pos = buf.find(JPG_SIG)
                    if pos == -1:
                        buf = buf[-(len(JPG_SIG) - 1):]
                        break

                    fin = buf.find(JPG_END, pos + 3)

                    if fin == -1:
                        if len(buf) - pos > MAX_JPG:
                            buf = buf[pos + 3:]
                            continue
                        buf = buf[pos:]
                        break

                    fin += len(JPG_END)
                    datos = buf[pos:fin]

                    if len(datos) > 5000:  # ignorar fragmentos muy pequenos
                        nombre = os.path.join(OUTPUT, f'foto_{count:04d}.jpg')
                        with open(nombre, 'wb') as f:
                            f.write(datos)
                        count += 1
                        print(f"  [+] Encontrada: foto_{count:04d}.jpg  ({len(datos)//1024} KB)")

                    buf = buf[fin:]

                if ticker % 250 == 0:
                    print(f"  ... {leidos / (1024**3):.1f} GB escaneados | {count} fotos recuperadas")

    except PermissionError:
        print("\n  ERROR: Abre el CMD como Administrador e intenta de nuevo.")
        sys.exit(1)
    except Exception as e:
        print(f"\n  Error: {e}")

    print("\n" + "=" * 50)
    print(f"  Listo! {count} fotos JPG guardadas en:")
    print(f"  {OUTPUT}")
    print("=" * 50)

if __name__ == '__main__':
    recover()
