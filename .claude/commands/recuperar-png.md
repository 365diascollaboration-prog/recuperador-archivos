# Skill: Recuperar PNG

Recupera imagenes PNG borradas del disco duro.

## Pasos

1. Verificar Python: `python --version`
2. Preguntar disco destino (letra diferente a C:)
3. Si el usuario quiere carpeta personalizada, editar la variable `OUTPUT` en `scripts/recuperar_png.py`
4. Decirle al usuario que abra CMD como Administrador y ejecute:

```
python scripts/recuperar_png.py
```

5. Explicar que cuando aparezca `[+] Encontrado: logo_XXXX.png` significa que encontro un archivo
6. Cuando termine o el usuario pare con Ctrl+C, abrir la carpeta destino en vista de iconos grandes para revisar los resultados
7. Advertir que habra archivos del sistema mezclados — es normal, buscar entre ellos los que necesitan
