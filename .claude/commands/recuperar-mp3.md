# Skill: Recuperar Musica

Recupera archivos de musica MP3, OGG y FLAC borrados del disco duro.

## Pasos

1. Verificar Python: `python --version`
2. Preguntar disco destino (letra diferente a C:)
3. Si el usuario quiere carpeta personalizada, editar `OUTPUT` en `scripts/recuperar_mp3.py`
4. Decirle que abra CMD como Administrador y ejecute:

```
python scripts/recuperar_mp3.py
```

5. El script busca la firma ID3 que tienen la mayoria de canciones MP3
6. Archivos menores de 50KB se ignoran para evitar fragmentos cortos sin valor
7. Cuando termine, reproducir las canciones para verificar que esten completas
8. Si una cancion suena cortada al final es normal — el fin del archivo puede estar sobreescrito
