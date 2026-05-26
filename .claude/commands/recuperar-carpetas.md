# Skill: Recuperar Carpetas con Estructura Original

Recupera archivos borrados conservando la estructura de carpetas original
leyendo directamente la MFT (Master File Table) de NTFS.

## Diferencia con los otros scripts

Los otros scripts recuperan archivos sueltos por firma binaria.
Este script lee el indice del disco (MFT) y reconstruye:

```
📁 Mi Proyecto/
   📁 Logos/
      logo_principal.png
   📁 Fotos/
      foto1.jpg
   documento.pdf
```

En vez de archivos sin nombre ni carpeta de origen.

## Pasos

1. Verificar Python: `python --version`
2. Advertir que el proceso puede tardar 30-60 minutos
3. Asegurarse que el disco destino tenga espacio suficiente
4. Abrir CMD como Administrador y ejecutar:

```
python scripts/recuperar_carpetas.py
```

5. El script primero lee el boot sector para ubicar la MFT
6. Luego escanea todas las entradas de la MFT buscando archivos borrados
7. Reconstruye las rutas originales usando las referencias de carpeta padre
8. Extrae los archivos con sus nombres y estructura original

## Advertencias

- Requiere CMD como Administrador obligatoriamente
- Los archivos cuyo contenido fue sobreescrito apareceran vacios o corruptos
- Archivos de sistema (que empiezan con $) se omiten automaticamente
- Si una carpeta padre tambien fue borrada, se crea igual en el destino

## Cuando termina

Revisar la carpeta:
```
D:\omnibook 2026 nano\Carpetas_recuperadas\
```

Los archivos apareceran organizados en sus carpetas originales.
