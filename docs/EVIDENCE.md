# Plan de ficha de evidencias — NO es la ficha final

Entrega EVA exactamente: URL del repositorio, `eva1_apellidos_nombres.zip` y
`eva1_apellidos_nombres.pdf`. Ya hay repositorio, cinco commits, Draft PR y CI
verificados; faltan identidad de entrega, materiales oficiales y evidencias AWS.
No se genera PDF final para aparentar revisión humana o E05–E08 ejecutados.

La ficha final tendrá ocho evidencias significativas (dentro del rango 6–8),
Arial 11, interlineado 1,5, alineación izquierda y páginas numeradas. Prepararla
en procesador de texto y exportar PDF; inspeccionar fuente/interlineado/paginación
y legibilidad después de exportar. No convertir este plan directamente en entrega.
Antes de maquetar, solicitar/cotejar la **plantilla oficial de la Ficha**; el formato
anterior proviene de los requisitos comunicados, no de un archivo docente recibido.

| ID | Qué demuestra y fuente real requerida | CE | Estado |
|---|---|---|---|
| E01 | URL, árbol y git status/log del repositorio local/remoto | CE3 | Cinco commits desde main; base e7f6025; ajuste lista 8 local sin commit |
| E02 | Código módulos, variables, outputs, dependencias y diagrama | CE1, CE2 | Tres módulos; lista 8, tag y prueba preparados; faltan plantilla/configuración institucional |
| E03 | Branch, commits SHA, PR y revisión humana/resolución | CE3, CE4 | Draft PR #1 real abierta, 0 reviews; revisión humana pendiente |
| E04 | Cinco controles diferenciados, aserciones y resultados con exit codes | CE6 | Dos ejecuciones success y cuatro checks en e7f6025; preparación local exige CI de su SHA |
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

## Texto base de la Ficha — ocho evidencias, borrador sin PDF

Cada bloque siguiente se trasladará a la plantilla docente cuando se confirme.
Las fuentes de GitHub se consultaron por GET el 24-10-2026; se guardaron snapshots
en `artifacts/predeploy/github-readonly.json` y `github-detail.json` (ignorados).
Las horas indicadas son America/Santiago, UTC−03:00. No se generaron capturas.

### E01 — Repositorio, estructura y trazabilidad (CE3)

Demuestra: organización del repositorio individual, tres módulos, tests, scripts,
documentación e historial trazable. Fuente: [repositorio](https://github.com/JoacoZun/nexoandes-iac-u1),
`git log main..HEAD`, `git diff main...HEAD --stat` y árbol de archivos.
Base publicada: `e7f6025bc8fd7e221942c19d3fd0eb579809410b`; cinco commits sobre
main, 46 archivos en la implementación publicada. Fechas: 24-10-2026,
11:54:46–12:14:36. Agregar captura legible del árbol/log y el SHA final tras
publicar los cambios locales; no atribuir la preparación lista 8 a e7f6025.

### E02 — Arquitectura y Terraform modular (CE1, CE2)

Demuestra: VPC 172.16.0.0/16, subnet derivada del input X, IGW/ruta/asociación,
SG HTTP sin SSH y EC2 con IMDSv2/EBS cifrado. Fuente: `main.tf`, `variables.tf`,
`outputs.tf` y `modules/`; commit de infraestructura
[`86dc894`](https://github.com/JoacoZun/nexoandes-iac-u1/commit/86dc894e8c257649a07868f733d606c0f5f642cf).
La preparación local del 24-10-2026 configura default X=8, subnet 172.16.8.0/24
y tag ListNumber derivado; el caso de prueba X=255 permanece para reutilización.
Agregar SHA del cambio lista 8 y captura de sus assertions cuando pase CI. Faltan
plantilla oficial y comprobación funcional del portal; el diagrama es diseño,
no evidencia de recursos creados.

### E03 — Rama, commits y revisión (CE3, CE4)

Demuestra: feature/fase1-iac separada de main y
[Draft PR #1](https://github.com/JoacoZun/nexoandes-iac-u1/pull/1), abierta a
main, creada el 24-10-2026 a las 12:26:12. Head e7f6025; base 7869232.
Commits: 86dc894 (infra), b5494aa (tests), 3f274f0 (CI), 1c0966c (docs) y
e7f6025 (lock Linux). SHAs completos y comparación en PULL_REQUEST.md.
Fuente: PR, [archivos comparados](https://github.com/JoacoZun/nexoandes-iac-u1/pull/1/files)
y API de reviews: **0 revisiones registradas**. Agregar comentarios/resolución,
identidad y fecha del revisor humano cuando existan. No se acredita aprobación.

### E04 — Controles automatizados (CE6)

Demuestra: CI real sin AWS sobre e7f6025. Dos ejecuciones, cuatro checks success:

| Evento y hora de inicio (24-10-2026) | Run | Check controls | Check repository-python |
|---|---|---|---|
| push, 12:14:48 | [40106088973](https://github.com/JoacoZun/nexoandes-iac-u1/actions/runs/40106088973) | [120907958411](https://github.com/JoacoZun/nexoandes-iac-u1/actions/runs/40106088973/job/120907958411) | [120907958568](https://github.com/JoacoZun/nexoandes-iac-u1/actions/runs/40106088973/job/120907958568) |
| pull_request, 12:26:17 | [40106962247](https://github.com/JoacoZun/nexoandes-iac-u1/actions/runs/40106962247) | [120910540303](https://github.com/JoacoZun/nexoandes-iac-u1/actions/runs/40106962247/job/120910540303) | [120910540105](https://github.com/JoacoZun/nexoandes-iac-u1/actions/runs/40106962247/job/120910540105) |

La API confirmó success en init, formato, validate, pruebas con mocks, lint,
seguridad y política; el job Python independiente también pasó. Las ocho pruebas
están declaradas en el código; para mostrar la salida literal `8 passed` adjuntar
el log/captura del paso del job o del Git Bash real. No se descargaron logs de
Actions autenticados ni se inventó su contenido. Los resultados locales nuevos
en Codex se documentan aparte en VALIDATION.md, incluidos sus bloqueos mTLS.
Agregar run/checks del futuro SHA lista 8 antes de la ficha final.

### E05 — Pipeline, plan y aprobación (CE5)

Demuestra por ahora solo diseño: CI activo y candidato `deploy.yml.disabled`,
plan guardado vinculado a SHA/digest/edad, concurrencia y environment previsto.
Fuente: workflow candidato, PIPELINE.md y commit 3f274f0; auditoría 24-10-2026.
Pendiente para evidencia de ejecución: guía autorizada, backend/auth, almacén de
planes protegido, configuración efectiva del gate, run ID, SHA/hash del plan,
persona/fecha de aprobación y enlace a la ejecución. No confundir Draft PR con gate.

### E06 — Despliegue automatizado y state (CE7)

PENDIENTE. Incorporar solo después de autorización: run ID y SHA de apply,
identidad temporal saneada, cuenta/región autorizadas, backend/locking realmente
utilizados, plan aprobado y outputs de recursos. Fuente futura: pipeline/AWS real.
Fecha e IDs aún no existen; no completar con ejemplos o resultados de mocks.

### E07 — Verificación independiente (CE2, CE8)

PENDIENTE. Reunir terraform output, consulta AWS del MISMO Instance ID/IP,
HTTP 200 con marcador de la plantilla oficial y plan posterior sin cambios
inesperados (o explicación). Fuente futura: scripts/Verify-Deployment.ps1 y CLI
real, con fecha, SHA, run ID y evidencia saneada. Apply exitoso no basta.

### E08 — Limpieza, protección y entrega (CE8)

PENDIENTE de ejecución AWS. Reunir plan de destrucción autorizado y su hash,
aprobación, destroy por mecanismo institucional, consulta AWS independiente de
ausencia/terminación y comprobación de state. Añadir manifiesto/hash del ZIP
final inspeccionado, incluyendo lock y ejemplo público, excluyendo state/planes/
credenciales. Ver OPERATIONS.md y Build-Submission.ps1. La previsualización local
del ZIP no acredita destrucción ni constituye entrega EVA definitiva.

Referencias APA 7 y declaración de uso de ChatGPT/Codex: usar las del README y
agregar guía/plantilla institucional cuando se reciban, con autor/título/fecha reales.
Declarar apoyo de IA y revisión responsable del estudiante; no inventar autoría,
capturas, commits, revisión, aprobaciones o resultados de AWS.

Texto de declaración preparado: «Utilicé ChatGPT y Codex como herramientas de apoyo
para análisis, generación de código, revisión, pruebas y documentación. Revisé las
decisiones técnicas y distingo código, mocks, ejecuciones CI y evidencias AWS. No
presento revisiones automáticas como aprobación humana ni resultados simulados
como recursos o verificaciones reales». Adaptar solo para reflejar el uso efectivo.

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
La única excepción pública de variables es el archivo exacto
`terraform.tfvars.example`, revisado sin secretos. Los `.tfvars` reales siguen
excluidos; no convertir esa excepción en permiso general para incluir variables.

No se ha generado ZIP final sin nombre real ni PDF final sin evidencias verificables.
