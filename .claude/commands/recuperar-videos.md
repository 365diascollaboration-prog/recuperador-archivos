# Skill: Recuperar Videos

Recupera videos MP4, MOV, MKV y WEBM borrados del disco duro.

## Pasos

1. Verificar Python: `python --version`
2. Advertir que videos pueden pesar mucho — asegurarse que el disco destino tenga espacio suficiente
3. Preguntar disco destino (letra diferente a C:)
4. Si el usuario quiere carpeta personalizada, editar `OUTPUT` en `scripts/recuperar_videos.py`
5. Decirle que abra CMD como Administrador y ejecute:

```
python scripts/recuperar_videos.py
```

6. Cuando aparezca `[+] video_XXXX.mp4` con los MB va encontrando videos
7. Los videos pueden tardar mas en recuperarse por su tamano
8. Si aparecen videos corruptos al reproducirlos es normal — algunos sectores pueden estar sobreescritos parcialmente
9. Recomendar VLC para reproducir los archivos recuperados ya que tolera mejor archivos dañados
