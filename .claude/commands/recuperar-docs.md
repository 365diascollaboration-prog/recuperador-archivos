# Skill: Recuperar Documentos

Recupera documentos PDF, Word .doc y Word .docx borrados del disco duro.

## Pasos

1. Verificar Python: `python --version`
2. Preguntar disco destino (letra diferente a C:)
3. Si el usuario quiere carpeta personalizada, editar `OUTPUT` en `scripts/recuperar_docs.py`
4. Decirle que abra CMD como Administrador y ejecute:

```
python scripts/recuperar_docs.py
```

5. El script muestra el conteo separado: PDF / DOC / DOCX
6. Cuando termine, abrir los documentos con Word o Adobe Reader para verificar que esten completos
7. Si un PDF aparece corrupto, intentar abrirlo con el navegador (Chrome/Edge) que toleran mejor los PDFs dañados

## Nota sobre DOCX

Los archivos .docx son ZIP internamente. El script verifica que contengan estructura de Word antes de guardarlos, pero puede haber falsos positivos mezclados con otros archivos ZIP del sistema.
