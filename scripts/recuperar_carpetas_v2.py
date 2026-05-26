import os
import sys
import struct

MFT_ENTRY_SIZE = 1024
FILE_SIG       = b'FILE'
ATTR_FILE_NAME = 0x30
ATTR_DATA      = 0x80
ATTR_END       = 0xFFFFFFFF
FLAG_IN_USE    = 0x01
FLAG_DIRECTORY = 0x02
OUTPUT         = r'D:\omnibook 2026 nano\Carpetas_v2'

# ─── Firmas binarias por extension ───────────────────────────────────────────
# (offset_donde_buscar, firma)
FIRMAS = {
    '.png':  (0,  b'\x89PNG\r\n\x1a\n'),
    '.jpg':  (0,  b'\xff\xd8\xff'),
    '.jpeg': (0,  b'\xff\xd8\xff'),
    '.mp4':  (4,  b'ftyp'),
    '.mov':  (4,  b'ftyp'),
    '.mkv':  (0,  b'\x1a\x45\xdf\xa3'),
    '.pdf':  (0,  b'%PDF'),
    '.doc':  (0,  b'\xd0\xcf\x11\xe0'),
    '.docx': (0,  b'PK\x03\x04'),
    '.mp3':  (0,  b'ID3'),
    '.ogg':  (0,  b'OggS'),
    '.flac': (0,  b'fLaC'),
    '.svg':  (0,  b'<svg'),
    '.eps':  (0,  b'%!PS'),
    '.ai':   (0,  b'%AI'),
    '.html': (0,  b'<!DO'),
    '.htm':  (0,  b'<!DO'),
    '.zip':  (0,  b'PK\x03\x04'),
    '.gif':  (0,  b'GIF8'),
    '.bmp':  (0,  b'BM'),
    '.webp': (8,  b'WEBP'),
}

def validar_contenido(data, ext):
    """Verifica que el contenido tenga la firma correcta para su extension."""
    ext = ext.lower()
    if ext not in FIRMAS:
        return True  # extension desconocida: confiar en la MFT
    offset, firma = FIRMAS[ext]
    if len(data) < offset + len(firma):
        return False
    return data[offset:offset + len(firma)] == firma


# ─── Disco ────────────────────────────────────────────────────────────────────

class Disco:
    def __init__(self, ruta):
        self.f = open(ruta, 'rb')

    def leer(self, offset, size):
        try:
            self.f.seek(offset)
            return self.f.read(size)
        except Exception:
            return b''

    def cerrar(self):
        self.f.close()


# ─── Boot sector ──────────────────────────────────────────────────────────────

def leer_boot(disco):
    boot = disco.leer(0, 512)
    bps  = struct.unpack_from('<H', boot, 0x0B)[0]
    spc  = struct.unpack_from('<B', boot, 0x0D)[0]
    bpc  = bps * spc
    mft_cluster = struct.unpack_from('<Q', boot, 0x30)[0]
    mft_offset  = mft_cluster * bpc
    print(f"  Bytes/sector:{bps}  Sectores/cluster:{spc}  MFT:{hex(mft_offset)}")
    return bps, bpc, mft_offset


# ─── Fixup ────────────────────────────────────────────────────────────────────

def aplicar_fixup(data, bps):
    usa_off  = struct.unpack_from('<H', data, 4)[0]
    usa_size = struct.unpack_from('<H', data, 6)[0]
    data     = bytearray(data)
    usa_val  = struct.unpack_from('<H', data, usa_off)[0]
    for i in range(1, usa_size):
        pos = i * bps - 2
        if pos + 1 < len(data):
            if struct.unpack_from('<H', data, pos)[0] == usa_val:
                rep = struct.unpack_from('<H', data, usa_off + i * 2)[0]
                struct.pack_into('<H', data, pos, rep)
    return bytes(data)


# ─── Data runs ────────────────────────────────────────────────────────────────

def parsear_runs(runs_data):
    runs, pos, lcn = [], 0, 0
    while pos < len(runs_data):
        hdr = runs_data[pos]
        if hdr == 0:
            break
        len_b = hdr & 0x0F
        off_b = (hdr >> 4) & 0x0F
        pos  += 1
        if len_b == 0:
            break
        longitud = int.from_bytes(runs_data[pos:pos+len_b], 'little')
        pos += len_b
        if off_b > 0:
            raw   = runs_data[pos:pos+off_b]
            delta = int.from_bytes(raw, 'little')
            if raw[-1] & 0x80:
                delta -= (1 << (off_b * 8))
            lcn  += delta
            pos  += off_b
        runs.append((lcn, longitud))
    return runs


def leer_runs(disco, runs, size, bpc):
    data = b''
    for lcn, length in runs:
        chunk = disco.leer(lcn * bpc, length * bpc)
        data += chunk
        if len(data) >= size:
            break
    return data[:size]


# ─── Parsear entrada MFT ─────────────────────────────────────────────────────

def parsear_entrada(data, num, bps):
    if len(data) < 48 or data[:4] != FILE_SIG:
        return None
    try:
        data = aplicar_fixup(data, bps)
    except Exception:
        return None

    flags    = struct.unpack_from('<H', data, 22)[0]
    in_use   = bool(flags & FLAG_IN_USE)
    is_dir   = bool(flags & FLAG_DIRECTORY)
    attr_off = struct.unpack_from('<H', data, 20)[0]

    info = {
        'num': num, 'in_use': in_use, 'is_dir': is_dir,
        'nombres': [], 'padre': None,
        'runs': [], 'size': 0, 'residente': None,
    }

    pos = attr_off
    while pos < len(data) - 4:
        tipo  = struct.unpack_from('<I', data, pos)[0]
        if tipo == ATTR_END or tipo == 0:
            break
        largo = struct.unpack_from('<I', data, pos + 4)[0]
        if largo == 0 or largo > len(data) - pos:
            break
        no_res = data[pos + 8]

        if tipo == ATTR_FILE_NAME and not no_res:
            voff  = struct.unpack_from('<H', data, pos + 20)[0]
            vs    = pos + voff
            padre = struct.unpack_from('<Q', data, vs)[0] & 0xFFFFFFFFFFFF
            nlen  = data[vs + 64]
            ns    = data[vs + 65]
            ne    = vs + 66 + nlen * 2
            if ne <= len(data):
                try:
                    nombre = data[vs+66:ne].decode('utf-16-le')
                    info['nombres'].append((ns, nombre))
                    info['padre'] = padre
                except Exception:
                    pass

        elif tipo == ATTR_DATA:
            if no_res:
                roff  = struct.unpack_from('<H', data, pos + 32)[0]
                asize = struct.unpack_from('<Q', data, pos + 48)[0]
                info['runs'] = parsear_runs(data[pos + roff:pos + largo])
                info['size'] = asize
            else:
                vlen = struct.unpack_from('<I', data, pos + 16)[0]
                voff = struct.unpack_from('<H', data, pos + 20)[0]
                info['residente'] = data[pos + voff:pos + voff + vlen]
                info['size'] = vlen

        pos += largo
    return info


# ─── Nombre y ruta ────────────────────────────────────────────────────────────

def mejor_nombre(entry):
    if not entry['nombres']:
        return None
    for ns, name in entry['nombres']:
        if ns in (1, 3):
            return name
    return entry['nombres'][0][1]


def construir_ruta(num, entradas, depth=0):
    if depth > 20:
        return 'recuperado'
    entry = entradas.get(num)
    if not entry:
        return 'recuperado'
    nombre = mejor_nombre(entry)
    if not nombre:
        return f'entrada_{num}'
    padre = entry.get('padre')
    if padre is None or padre == num or padre <= 5:
        return nombre
    return os.path.join(construir_ruta(padre, entradas, depth + 1), nombre)


# ─── Escanear MFT ────────────────────────────────────────────────────────────

def escanear_mft(disco, mft_offset, bps):
    entradas = {}
    num      = 0
    borrados = 0
    vacios   = 0

    print("  Escaneando MFT...")

    while True:
        offset = mft_offset + num * MFT_ENTRY_SIZE
        data   = disco.leer(offset, MFT_ENTRY_SIZE)
        if len(data) < MFT_ENTRY_SIZE:
            break

        if data[:4] != FILE_SIG:
            vacios += 1
            if vacios > 5000:
                break
            num += 1
            continue

        vacios = 0
        info = parsear_entrada(data, num, bps)
        if info:
            entradas[num] = info
            if not info['in_use']:
                borrados += 1

        num += 1
        if num % 50000 == 0:
            print(f"  ... {num:,} entradas | {borrados:,} borradas")

    print(f"  Total: {num:,} entradas | {borrados:,} borradas")
    return entradas


# ─── Extraer con validacion ───────────────────────────────────────────────────

def extraer_validado(disco, entradas, bpc, output):
    os.makedirs(output, exist_ok=True)

    borrados = [
        (n, e) for n, e in entradas.items()
        if not e['in_use'] and not e['is_dir']
    ]

    print(f"\n  {len(borrados):,} archivos borrados encontrados.")
    print(f"  Extrayendo solo los que tienen contenido valido...\n")

    extraidos  = 0
    omitidos   = 0
    sin_firma  = 0

    stats = {}

    for num, entry in borrados:
        nombre = mejor_nombre(entry)
        if not nombre or nombre.startswith('$'):
            continue

        # Leer contenido
        try:
            if entry['residente'] is not None:
                data = entry['residente']
            elif entry['runs'] and entry['size'] > 0:
                data = leer_runs(disco, entry['runs'], entry['size'], bpc)
            else:
                continue
        except Exception:
            continue

        if not data or len(data) < 4:
            continue

        # Validar firma
        ext = os.path.splitext(nombre)[1].lower()
        if not validar_contenido(data, ext):
            omitidos += 1
            continue

        if ext not in FIRMAS:
            sin_firma += 1

        # Construir ruta y guardar
        ruta_rel  = construir_ruta(num, entradas)
        ruta_full = os.path.join(output, ruta_rel)
        os.makedirs(os.path.dirname(ruta_full), exist_ok=True)

        if os.path.exists(ruta_full):
            base, e2 = os.path.splitext(ruta_full)
            ruta_full = f"{base}_{num}{e2}"

        try:
            with open(ruta_full, 'wb') as f:
                f.write(data)
            extraidos += 1
            stats[ext] = stats.get(ext, 0) + 1

            kb = len(data) // 1024
            print(f"  [OK] {ruta_rel}  ({kb} KB)")

        except Exception:
            continue

    return extraidos, omitidos, sin_firma, stats


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  RECUPERADOR DE CARPETAS v2")
    print("  MFT + validacion de firmas binarias")
    print("  Solo guarda archivos con contenido real valido")
    print(f"  Destino: {OUTPUT}")
    print("=" * 60)

    if input("\n  Continuar? (s/n): ").strip().lower() != 's':
        sys.exit(0)

    try:
        disco = Disco(r'\\.\C:')
        bps, bpc, mft_offset = leer_boot(disco)
        entradas = escanear_mft(disco, mft_offset, bps)

        extraidos, omitidos, sin_firma, stats = extraer_validado(
            disco, entradas, bpc, OUTPUT
        )

        print("\n" + "=" * 60)
        print(f"  RESULTADO FINAL")
        print(f"  Extraidos (validos)  : {extraidos:,}")
        print(f"  Omitidos (basura)    : {omitidos:,}")
        print(f"  Sin firma conocida   : {sin_firma:,}")
        print()
        print("  Por tipo:")
        for ext, count in sorted(stats.items(), key=lambda x: -x[1]):
            print(f"    {ext or 'sin ext':10} → {count:,}")
        print()
        print(f"  Carpeta: {OUTPUT}")
        print("=" * 60)

    except PermissionError:
        print("\n  ERROR: Abre CMD como Administrador.")
    except Exception as e:
        print(f"\n  Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            disco.cerrar()
        except Exception:
            pass


if __name__ == '__main__':
    main()
