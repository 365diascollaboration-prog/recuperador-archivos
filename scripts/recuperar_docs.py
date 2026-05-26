import os
import sys

CHUNK    = 4 * 1024 * 1024       # 4MB por lectura
MAX_DOC  = 500 * 1024 * 1024     # 500MB maximo por documento
MIN_DOC  = 5 * 1024              # minimo 5KB
OUTPUT   = r'D:\omnibook 2026 nano\Documentos_recuperados'

# Firmas
PDF_SIG  = b'%PDF'
PDF_END  = b'%%EOF'
DOC_SIG  = b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'  # Word .doc / OLE2
DOCX_SIG = b'PK\x03\x04'                          # Word .docx (ZIP)
DOCX_CHK = b'word/'                               # verificacion dentro del ZIP

def es_docx(buf, pos):
    fragmento = buf[pos:pos + 512]
    return DOCX_CHK in fragmento

def buscar_sig(buf, desde=0):
    candidatos = []

    p = buf.find(PDF_SIG, desde)
    if p != -1:
        candidatos.append((p, '.pdf', 'pdf'))

    p = buf.find(DOC_SIG, desde)
    if p != -1:
        candidatos.append((p, '.doc', 'doc'))

    p = desde
    while True:
        p = buf.find(DOCX_SIG, p)
        if p == -1:
            break
        if es_docx(buf, p):
            candidatos.append((p, '.docx', 'docx'))
            break
        p += 4

    if not candidatos:
        return -1, '', ''

    candidatos.sort(key=lambda x: x[0])
    return candidatos[0]

def recover():
    os.makedirs(OUTPUT, exist_ok=True)
    count  = 0
    buf    = b''
    leidos = 0
    ticker = 0
    totales = {'pdf': 0, 'doc': 0, 'docx': 0}

    print("=" * 50)
    print("  RECUPERADOR DE DOCUMENTOS - Escaneando C:")
    print("  Formatos: PDF, Word .doc, Word .docx")
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
                    pos, ext, tipo = buscar_sig(buf)
                    if pos == -1:
                        buf = buf[-16:]
                        break

                    if tipo == 'pdf':
                        fin_idx = buf.find(PDF_END, pos + 4)
                        if fin_idx == -1:
                            if len(buf) - pos > MAX_DOC:
                                buf = buf[pos + 4:]
                                continue
                            buf = buf[pos:]
                            break
                        fin_idx += len(PDF_END) + 2
                        datos = buf[pos:fin_idx]
                    else:
                        siguiente, _, _ = buscar_sig(buf, pos + MIN_DOC)
                        if siguiente == -1:
                            if len(buf) - pos > MAX_DOC:
                                buf = buf[pos + 4:]
                                continue
                            buf = buf[pos:]
                            break
                        datos = buf[pos:siguiente]

                    if len(datos) >= MIN_DOC:
                        nombre = os.path.join(OUTPUT, f'doc_{count:04d}{ext}')
                        with open(nombre, 'wb') as f:
                            f.write(datos)
                        count += 1
                        totales[tipo] += 1
                        kb = len(datos) // 1024
                        print(f"  [+] doc_{count:04d}{ext}  ({kb} KB)")

                    buf = buf[pos + len(datos):]

                if ticker % 250 == 0:
                    print(f"  ... {leidos / (1024**3):.1f} GB | PDF:{totales['pdf']} DOC:{totales['doc']} DOCX:{totales['docx']}")

    except PermissionError:
        print("\n  ERROR: Abre el CMD como Administrador e intenta de nuevo.")
        sys.exit(1)
    except Exception as e:
        print(f"\n  Error: {e}")

    print("\n" + "=" * 50)
    print(f"  Listo! {count} documentos guardados en:")
    print(f"  {OUTPUT}")
    print(f"  PDF: {totales['pdf']} | DOC: {totales['doc']} | DOCX: {totales['docx']}")
    print("=" * 50)

if __name__ == '__main__':
    recover()
