import os
import sys

_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _dir)
try:
    from config import DISCO, OUTPUT_MUSICA as OUTPUT
except ImportError:
    DISCO  = r'\\.\C:'
    OUTPUT = r'D:\omnibook 2026 nano\Musica_recuperada'

CHUNK   = 4 * 1024 * 1024      # 4MB por lectura
MAX_MP3 = 200 * 1024 * 1024    # 200MB maximo por cancion
MIN_MP3 = 50 * 1024            # minimo 50KB
OUTPUT  = r'D:\omnibook 2026 nano\Musica_recuperada'

# Firmas de audio
ID3_SIG  = b'ID3'              # MP3 con etiqueta ID3 (mayoria de canciones)
MP3_SIG  = b'\xff\xfb'        # Frame MP3 sin ID3
MP3_SIG2 = b'\xff\xfa'        # Frame MP3 variante
OGG_SIG  = b'OggS'            # OGG Vorbis
FLAC_SIG = b'fLaC'            # FLAC

SIGS = [
    (ID3_SIG,  '.mp3'),
    (MP3_SIG,  '.mp3'),
    (MP3_SIG2, '.mp3'),
    (OGG_SIG,  '.ogg'),
    (FLAC_SIG, '.flac'),
]

def buscar_sig(buf, desde=0):
    mejor_pos = -1
    mejor_ext = ''

    for sig, ext in SIGS:
        pos = buf.find(sig, desde)
        if pos != -1 and (mejor_pos == -1 or pos < mejor_pos):
            mejor_pos = pos
            mejor_ext = ext

    return mejor_pos, mejor_ext

def recover():
    os.makedirs(OUTPUT, exist_ok=True)
    count  = 0
    buf    = b''
    leidos = 0
    ticker = 0
    totales = {'mp3': 0, 'ogg': 0, 'flac': 0}

    print("=" * 50)
    print("  RECUPERADOR DE MUSICA - Escaneando disco C:")
    print("  Formatos: MP3, OGG, FLAC")
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

                    siguiente, _ = buscar_sig(buf, pos + MIN_MP3)

                    if siguiente == -1:
                        if len(buf) - pos > MAX_MP3:
                            buf = buf[pos + 3:]
                            continue
                        buf = buf[pos:]
                        break

                    datos = buf[pos:siguiente]

                    if len(datos) >= MIN_MP3:
                        tipo = ext.replace('.', '')
                        nombre = os.path.join(OUTPUT, f'cancion_{count:04d}{ext}')
                        with open(nombre, 'wb') as f:
                            f.write(datos)
                        count += 1
                        totales[tipo] = totales.get(tipo, 0) + 1
                        mb = len(datos) // (1024 * 1024)
                        kb = len(datos) // 1024
                        size_str = f'{mb} MB' if mb > 0 else f'{kb} KB'
                        print(f"  [+] cancion_{count:04d}{ext}  ({size_str})")

                    buf = buf[siguiente:]

                if ticker % 250 == 0:
                    print(f"  ... {leidos / (1024**3):.1f} GB | MP3:{totales.get('mp3',0)} OGG:{totales.get('ogg',0)} FLAC:{totales.get('flac',0)}")

    except PermissionError:
        print("\n  ERROR: Abre el CMD como Administrador e intenta de nuevo.")
        sys.exit(1)
    except Exception as e:
        print(f"\n  Error: {e}")

    print("\n" + "=" * 50)
    print(f"  Listo! {count} archivos de musica guardados en:")
    print(f"  {OUTPUT}")
    print(f"  MP3: {totales.get('mp3',0)} | OGG: {totales.get('ogg',0)} | FLAC: {totales.get('flac',0)}")
    print("=" * 50)

if __name__ == '__main__':
    recover()
