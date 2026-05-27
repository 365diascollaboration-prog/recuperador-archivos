# Como funciona NTFS y por que se pueden recuperar archivos borrados

## El disco duro no borra nada

Cuando presionas Suprimir o vacías la papelera, Windows no toca los datos reales del disco. Solo hace dos cosas:

1. Marca el espacio del archivo como "disponible" en la MFT
2. Elimina la entrada del directorio

Los bytes del archivo siguen exactamente donde estaban. Hasta que otro archivo necesite ese espacio y los sobreescriba, son recuperables.

---

## Que es la MFT

La **Master File Table (MFT)** es el indice maestro de NTFS. Es un archivo especial (`$MFT`) que contiene una entrada por cada archivo y carpeta del disco.

Cada entrada MFT tiene 1024 bytes y guarda:
- Nombre del archivo
- Referencia a la carpeta padre
- Timestamps (creacion, modificacion, acceso)
- Donde estan los datos en el disco (data runs)
- Si el archivo esta activo o borrado (flag IN_USE)

Cuando borras un archivo, NTFS apaga el bit `IN_USE` de su entrada MFT. La entrada sigue ahi, con toda la informacion — solo marcada como disponible.

---

## Que son las firmas binarias (Magic Bytes)

Cada formato de archivo empieza con una secuencia de bytes fija que lo identifica. Ejemplos:

| Formato | Firma hex | Firma ASCII |
|---------|-----------|-------------|
| PNG | `89 50 4E 47 0D 0A 1A 0A` | `.PNG....` |
| JPEG | `FF D8 FF` | `...` |
| PDF | `25 50 44 46` | `%PDF` |
| MP4 | `66 74 79 70` en offset 4 | `ftyp` |
| ZIP | `50 4B 03 04` | `PK..` |
| MP3 | `49 44 33` | `ID3` |

Estas firmas no las pone el usuario — las escribe el programa que crea el archivo. Son parte del estandar del formato.

---

## Los dos metodos de recuperacion

### Metodo 1 — Busqueda por firma (recuperar_png.py, recuperar_jpg.py, etc.)

Lee el disco sector por sector buscando las firmas binarias. Cuando encuentra una, extrae los datos hasta el marcador de fin del archivo.

**Ventaja:** Encuentra archivos aunque la MFT ya no los tenga  
**Desventaja:** No sabe el nombre original ni la carpeta donde estaba

### Metodo 2 — Lectura de MFT (recuperar_carpetas_v2.py)

Lee directamente la MFT buscando entradas con el flag IN_USE apagado. Reconstruye la ruta original y extrae los datos siguiendo los data runs.

**Ventaja:** Recupera el nombre original y la estructura de carpetas  
**Desventaja:** Si los sectores fueron sobreescritos, el contenido es basura

### Metodo combinado (recuperar_carpetas_v2.py)

Lee la MFT para obtener nombres y rutas, pero antes de guardar valida que el contenido tenga la firma correcta para su extension. Si no coincide, descarta el archivo en vez de guardar basura.

---

## Por que algunos archivos se recuperan y otros no

| Situacion | Resultado |
|-----------|-----------|
| Borrado reciente, disco sin uso posterior | Recuperacion casi completa |
| Borrado reciente, instalaste programas despues | Recuperacion parcial |
| Borrado hace semanas con uso intenso del disco | Recuperacion baja o nula |
| Disco formateado (formato rapido) | MFT borrada pero datos pueden seguir |
| Disco formateado (formato completo) | Datos sobreescritos, recuperacion imposible |

---

## Por que aparecen caracteres chinos

Cuando un archivo encriptado o binario se abre como texto, el sistema intenta interpretar los bytes como caracteres Unicode. Los bytes aleatorios de datos encriptados (como los archivos DPAPI de Chrome) producen caracteres de idiomas asiaticos o simbolos extraños.

No es que el archivo este en chino. Es que sus bytes son binarios y no texto.

Ver: [Archivos encriptados de Chrome](archivos-encriptados-chrome.md)

---

## Data Runs — como NTFS sabe donde estan los datos

Cuando un archivo es grande, sus datos pueden estar en multiples lugares del disco (fragmentado). NTFS guarda esta informacion como **data runs**: una lista de pares (cluster_inicio, cantidad_de_clusters).

Ejemplo:
```
Run 1: empieza en cluster 1000, dura 50 clusters
Run 2: empieza en cluster 5000, dura 30 clusters
```

El archivo real son esos 80 clusters concatenados. `recuperar_carpetas_v2.py` sigue estos data runs para leer el contenido completo aunque este fragmentado.
