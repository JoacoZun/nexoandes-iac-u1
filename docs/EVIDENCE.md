# Plan de ficha de evidencias — NO es la ficha final

Entrega EVA exactamente: URL del repositorio, `eva1_apellidos_nombres.zip` y
`eva1_apellidos_nombres.pdf`. Identidad y evidencias reales aún incompletas.
No se genera un PDF final para aparentar E03/E05–E08 ejecutados.

La ficha final tendrá ocho evidencias significativas (dentro del rango 6–8),
Arial 11, interlineado 1,5, alineación izquierda y páginas numeradas. Prepararla
en procesador de texto y exportar PDF; inspeccionar fuente/interlineado/paginación
y legibilidad después de exportar. No convertir este plan directamente en entrega.

| ID | Qué demuestra y fuente real requerida | CE | Estado |
|---|---|---|---|
| E01 | URL, árbol y git status/log del repositorio local/remoto | CE3 | Auditoría local disponible; capturar estado final tras commits |
| E02 | Código módulos, variables, outputs, dependencias y diagrama | CE1, CE2 | Código local disponible; falta cerrar parámetros/plantilla |
| E03 | Branch, commits SHA, PR y revisión humana/resolución | CE3, CE4 | Pendiente autorización y ejecución Git |
| E04 | Cinco controles diferenciados, aserciones y resultados con exit codes | CE6 | Consultar VALIDATION.md; pipeline remoto pendiente |
| E05 | Trigger/init/plan, SHA/hash y gate real con aprobador/run ID | CE5 | Solo candidato; sin ejecución ni gate configurado |
| E06 | Apply automatizado, identidad temporal saneada, backend/locking | CE7 | Pendiente autorización y ejecución AWS |
| E07 | Outputs y AWS mismo ID/IP, HTTP contenido oficial, plan posterior | CE2, CE8 | Pendiente despliegue |
| E08 | Destroy autorizado, consulta AWS de ausencia y ZIP inspeccionado | CE8 | Procedimiento preparado; sin ejecución |

Cada evidencia incluirá: título/ID, qué demuestra, fuente concreta (archivo + líneas,
comando/log o URL), fecha/hora con zona, resultado observado, CE, SHA relevante,
PR/run ID cuando corresponda y explicación breve. No basta con ocho capturas del
mismo control. Ocultar tokens, claves, state, detalles sensibles del plan y datos
personales innecesarios; conservar original protegido cuando sea exigido.

Bitácora inicial (24-10-2026, America/Santiago): Terraform inicial estaba vacío;
Git sandbox reportó propietario distinto (resuelto con safe.directory por comando);
Terraform instalado requirió ejecución fuera de sandbox; pruebas requirieron
repetir init tras añadir módulos de test. Agregar incidencias reales de validación
y su resolución desde VALIDATION.md, sin copiar fallos inexistentes.

Referencias APA 7 y declaración de uso de ChatGPT/Codex: usar las del README y
agregar guía/plantilla institucional cuando se reciban, con autor/título/fecha reales.
Declarar apoyo de IA y revisión responsable del estudiante; no inventar autoría,
capturas, commits, revisión, aprobaciones o resultados de AWS.

## ZIP limpio

Solo al cerrar proyecto y revisar archivos:

```powershell
powershell.exe -NoProfile -ExecutionPolicy RemoteSigned -File scripts/Build-Submission.ps1 -Preview
powershell.exe -NoProfile -ExecutionPolicy RemoteSigned -File scripts/Build-Submission.ps1 -ApellidosNombres 'apellidos_nombres_reales'
Get-Content dist/zip-manifest.txt
Get-FileHash dist/eva1_apellidos_nombres_reales.zip -Algorithm SHA256
```

El script toma archivos versionados y nuevos no ignorados, permite extensiones de
proyecto y directorios definidos, incluye `.terraform.lock.hcl` y excluye herramientas,
Git, state/derivados, tfvars, planes, backend local y claves. El ZIP queda en dist
ignorado. Nunca usar ZIP indiscriminado de toda la carpeta. Inspeccionar contenido
extraído en carpeta temporal y buscar secretos, verificar plantilla oficial y lock.
No incluir PDF final dentro del ZIP si la entrega lo requiere separado.

No se ha generado ZIP final sin nombre real ni PDF final sin evidencias verificables.
