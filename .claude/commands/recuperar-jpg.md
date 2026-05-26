# Skill: Recuperar JPG

Recupera fotos JPG borradas del disco duro.

## Pasos

1. Verificar Python: `python --version`
2. Preguntar disco destino (letra diferente a C:)
3. Si el usuario quiere carpeta personalizada, editar `OUTPUT` en `scripts/recuperar_jpg.py`
4. Decirle que abra CMD como Administrador y ejecute:

```
python scripts/recuperar_jpg.py
```

5. Cuando aparezca `[+] Encontrada: foto_XXXX.jpg` va encontrando fotos
6. Las fotos muy pequenas (menos de 5KB) se ignoran automaticamente para evitar miniaturas del sistema
7. Cuando termine, revisar la carpeta destino en vista de iconos grandes
