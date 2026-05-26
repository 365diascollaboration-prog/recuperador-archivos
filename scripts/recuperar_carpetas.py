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
OUTPUT         = r'D:\omnibook 2026 nano\Carpetas_recuperadas'


# ─── Lectura del disco ────────────────────────────────────────────────────────

class Disco:
    def __init__(self, ruta):
        self.f = open(ruta, 'rb')

    def leer(self, offset, size):
        self.f.seek(offset)
        return self.f.read(size)

    def cerrar(self):
        self.f.close()


# ─── Boot Sector ─────────────────────────────────────────────────────────────

def leer_boot(disco):
    boot = disco.leer(0, 512)
    bps  = struct.unpack_from('<H', boot, 0x0B)[0]   # bytes por sector
    spc  = struct.unpack_from('<B', boot, 0x0D)[0]   # sectores por cluster
    bpc  = bps * spc                                  # bytes por cluster
    mft_cluster = struct.unpack_from('<Q', boot, 0x30)[0]
    mft_offset  = mft_cluster * bpc
    print(f"  Bytes/sector: {bps} | Sectores/cluster: {spc} | MFT en: {hex(mft_offset)}")
    return bps, bpc, mft_offset


# ─── Fixup (corrección de sectores) ──────────────────────────────────────────

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


# ─── Data Runs (archivos no-residentes) ──────────────────────────────────────

def parsear_runs(runs_data):
    runs, pos, lcn = [], 0, 0
    while pos < len(runs_data):
        hdr = runs_data[pos]
        if hdr == 0:
            break
        len_b = hdr & 0x0F
        off_b = (hdr >> 4) & 0x0F
        pos += 1
        if len_b == 0:
            break
        longitud = int.from_bytes(runs_data[pos:pos+len_b], 'little')
        pos += len_b
        if off_b > 0:
            raw = runs_data[pos:pos+off_b]
            delta = int.from_bytes(raw, 'little')
            if raw[-1] & 0x80:
                delta -= (1 << (off_b * 8))
            lcn += delta
            pos += off_b
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
        tipo = struct.unpack_from('<I', data, pos)[0]
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


# ─── Nombre optimo ────────────────────────────────────────────────────────────

def mejor_nombre(entry):
    if not entry['nombres']:
        return None
    for ns, name in entry['nombres']:
        if ns in (1, 3):
            return name
    return entry['nombres'][0][1]


# ─── Construir ruta ───────────────────────────────────────────────────────────

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
    entradas  = {}
    num       = 0
    borrados  = 0
    vacios    = 0

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

    print(f"  Total: {num:,} entradas | {borrados:,} archivos/carpetas borrados")
    return entradas, borrados


# ─── Extraer archivos borrados ────────────────────────────────────────────────

def extraer(disco, entradas, bpc, output):
    os.makedirs(output, exist_ok=True)
    extraidos = 0
    errores   = 0

    borrados = [
        (n, e) for n, e in entradas.items()
        if not e['in_use'] and not e['is_dir']
    ]

    print(f"\n  Extrayendo {len(borrados):,} archivos...")

    for num, entry in borrados:
        nombre = mejor_nombre(entry)
        if not nombre or nombre.startswith('$'):
            continue

        ruta_rel  = construir_ruta(num, entradas)
        ruta_full = os.path.join(output, ruta_rel)
        os.makedirs(os.path.dirname(ruta_full), exist_ok=True)

        try:
            if entry['residente'] is not None:
                data = entry['residente']
            elif entry['runs'] and entry['size'] > 0:
                data = leer_runs(disco, entry['runs'], entry['size'], bpc)
            else:
                continue

            if not data:
                continue

            if os.path.exists(ruta_full):
                base, ext = os.path.splitext(ruta_full)
                ruta_full = f"{base}_{num}{ext}"

            with open(ruta_full, 'wb') as f:
                f.write(data)

            extraidos += 1
            if extraidos % 200 == 0:
                print(f"  [+] {extraidos:,} archivos extraidos...")

        except Exception:
            errores += 1

    return extraidos, errores


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  RECUPERADOR DE CARPETAS")
    print("  Lee la MFT de NTFS y reconstruye la estructura original")
    print(f"  Destino: {OUTPUT}")
    print("=" * 60)

    if input("\n  Continuar? (s/n): ").strip().lower() != 's':
        sys.exit(0)

    try:
        disco = Disco(r'\\.\C:')
        bps, bpc, mft_offset = leer_boot(disco)

        entradas, borrados = escanear_mft(disco, mft_offset, bps)

        if borrados == 0:
            print("\n  No se encontraron archivos borrados.")
            return

        print(f"\n  {borrados:,} archivos borrados encontrados.")
        if input("  Extraer con estructura de carpetas? (s/n): ").strip().lower() != 's':
            return

        extraidos, errores = extraer(disco, entradas, bpc, OUTPUT)

        print("\n" + "=" * 60)
        print(f"  Extraidos : {extraidos:,}")
        print(f"  Errores   : {errores:,}")
        print(f"  Carpeta   : {OUTPUT}")
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
