import os
import sys

PNG_SIG = b'\x89PNG\r\n\x1a\n'
IEND    = b'IEND\xaeB`\x82'
CHUNK   = 4 * 1024 * 1024   # 4MB por lectura
MAX_PNG = 50 * 1024 * 1024  # maximo 50MB por PNG
OUTPUT  = r'D:\omnibook 2026 nano\PNGs_recuperados'

def recover():
    os.makedirs(OUTPUT, exist_ok=True)
    count   = 0
    buf     = b''
    leidos  = 0
    ticker  = 0

    print("=" * 50)
    print("  RECUPERADOR DE PNG - Escaneando disco C:")
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
                    pos = buf.find(PNG_SIG)
                    if pos == -1:
                        buf = buf[-(len(PNG_SIG) - 1):]
                        break

                    fin = buf.find(IEND, pos + 8)

                    if fin == -1:
                        if len(buf) - pos > MAX_PNG:
                            buf = buf[pos + 8:]
                            continue
                        buf = buf[pos:]
                        break

                    fin += len(IEND)
                    datos = buf[pos:fin]
                    nombre = os.path.join(OUTPUT, f'logo_{count:04d}.png')
                    with open(nombre, 'wb') as f:
                        f.write(datos)
                    count += 1
                    print(f"  [+] Encontrado: logo_{count:04d}.png  ({len(datos)//1024} KB)")
                    buf = buf[fin:]

                if ticker % 250 == 0:
                    print(f"  ... {leidos / (1024**3):.1f} GB escaneados | {count} PNG recuperados")

    except PermissionError:
        print("\n  ERROR: Abre el CMD como Administrador e intenta de nuevo.")
        sys.exit(1)
    except Exception as e:
        print(f"\n  Error: {e}")

    print("\n" + "=" * 50)
    print(f"  Listo! {count} archivos PNG guardados en:")
    print(f"  {OUTPUT}")
    print("=" * 50)

if __name__ == '__main__':
    recover()
