# Archivos .tmp de Chrome encriptados con DPAPI

## El caso real

Durante una recuperacion de archivos borrados encontramos este archivo:

```
290a7458-13af-450e-9279-08e90d59a0d5.tmp
```

Ubicado en:
```
AppData\Local\Google\Chrome\User Data\Profile 1\
```

Al analizarlo los primeros bytes eran:
```
0E B8 03 F5 A6 3A 21 CF 56 52 6D 63 D5 A3 14 25...
```

No coincide con ninguna firma conocida. No es texto. No es imagen. No es video.

## Por que parece "chino" o basura

Cuando recuperas archivos borrados del disco, algunos tienen contenido binario encriptado que los visores de texto intentan mostrar como caracteres Unicode — resultando en simbolos como `陝᧊⯇⑹` o caracteres CJK aleatorios.

Eso no significa que el archivo este dañado. Significa que **esta encriptado a proposito**.

## Que es DPAPI

**DPAPI** (Data Protection API) es el sistema de cifrado de Windows que protege datos sensibles atandolos a la cuenta del usuario actual.

Chrome usa DPAPI para encriptar:
- Cookies de sesion
- Contrasenas guardadas
- Historial de navegacion
- Datos de autocompletado
- Preferencias del perfil
- Tokens de sesion

La clave de cifrado esta derivada de las credenciales de tu cuenta de Windows. Sin esa clave — y sin la misma sesion de usuario — el archivo es indescifrable.

## Por que tiene nombre GUID

Chrome usa el patron de **escritura atomica**:

```
1. Escribe datos nuevos en archivo temporal (GUID.tmp)
2. Si la escritura es exitosa → renombra a archivo final
3. Si algo falla → el .tmp queda huerfano
```

Cuando Chrome se cierra de golpe, se desinstala, o la carpeta es borrada durante una escritura, los archivos `.tmp` quedan abandonados con su nombre GUID original.

## Como identificar estos archivos

Usa el script `scripts/identificar_archivo.py` incluido en este repositorio:

```bash
python scripts/identificar_archivo.py "ruta\al\archivo.tmp"
```

Si el resultado es **"Datos encriptados DPAPI / Chrome"** significa que:
- El archivo es interno de Chrome
- Esta encriptado con tu clave de Windows
- No contiene tus fotos, logos ni documentos personales
- No puede ser descifrado sin la clave original

## Lo que debes hacer

**Ignorarlo.** No contiene tus archivos personales.

Los archivos que realmente te interesan — fotos, logos, documentos — tienen firmas binarias reconocibles y los recupera correctamente el script `recuperar_todo.py`.

## Leccion para la comunidad

Cuando recuperas archivos del disco vas a encontrar tres tipos:

| Tipo | Ejemplo | Que hacer |
|------|---------|-----------|
| Archivo valido | PNG, JPG, PDF con firma correcta | Guardar |
| Fragmento corrupto | Bytes aleatorios sin firma | Ignorar |
| Datos encriptados | Chrome DPAPI, BitLocker | Ignorar — no recuperable sin clave |

Nuestro script `recuperar_carpetas_v2.py` ya maneja esto automaticamente — valida la firma antes de guardar y descarta el resto.
