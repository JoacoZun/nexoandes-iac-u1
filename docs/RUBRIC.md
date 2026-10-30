# Revisión CE1–CE8

Estado actualizado al 27-10-2026. No se calculan puntos garantizados: corresponde al docente
evaluar evidencia final y guía institucional completa, que aún no está disponible.

## Matriz actual — integración local del portal oficial

Pesos de la evaluación, no puntajes obtenidos. HEAD local `9f4ceac`; PR #1 Draft.
La CI histórica comprobada no acredita la integración local posterior de la plantilla.

| Criterio/peso | Implementado | Validado realmente | Evidencia disponible | Pendiente y acción concreta |
|---|---|---|---|---|
| CE1 — 10 | Recursos/inputs/outputs/locals/data/dependencias; lista 8; contrato explícito de cinco parámetros | Auditoría local, cálculo subnet y controles según VALIDATION.md | Módulos, plantilla con hash, E02 | Completar identidad/región/tipo y repetir Terraform/CI del SHA final |
| CE2 — 25 | Tres módulos reutilizables; plantilla oficial renderizada y pasada a compute | Formato/controles estáticos locales; sin portal AWS probado | E02/E04, tests mock ampliados | Completar validate/test en entorno funcional, desplegar y demostrar portal; parcial |
| CE3 — 10 | Estructura, ignores, lock y seis commits sobre main hasta 9f4ceac | Git local corrobora historial; ZIP preview pendiente de repetir | E01, log y comparación main...HEAD | Registrar integración solo con autorización y conservar SHA/manifiesto final |
| CE4 — 10 | Rama feature y Draft PR #1 a main | Existencia/state/head/base comprobados; 0 reviews | E03, URL PR y comparación | Revisión humana real, comentarios/resolución y estado final autorizado; parcial, no aprobado |
| CE5 — 10 | CI activo con permisos mínimos y candidato protegido desactivado | Dos triggers reales; candidate/gate no ejecutados | E04/E05, workflows y PIPELINE.md | Recibir guía; definir auth/state/almacén del plan y configurar gate efectivo antes de activar; parcial |
| CE6 — 10 | Cinco controles, regresiones Python, hash y sintaxis de plantilla en CI | Resultados locales del 27-10 separados; CI histórica corresponde a un SHA anterior | E04 y VALIDATION.md | Ejecutar CI del SHA que contenga la plantilla y adjuntar logs legibles |
| CE7 — 10 | Adaptadores pendientes y flujo de apply diseñado | Ningún apply AWS ejecutado | Solo diseño; E06 pendiente | Autorización institucional, auth/backend/gate, plan revisado y apply automatizado real; pendiente |
| CE8 — 15 | Scripts AWS/HTTP/limpieza, exclusión de secretos y empaquetado limpio | Análisis estático/previsualización local; sin consultas AWS/HTTP/destroy reales | E07/E08 planificadas; scripts y manifestación local | Ejecutar verificación/limpieza autorizadas; inspeccionar ZIP/PDF final con Ficha oficial; parcial |

No se otorga total 100/100. CE1/CE3 y CE6 tienen evidencia de implementación/CI de
base; CE2/CE4/CE5/CE8 siguen parciales y CE7 no está ejecutado. La aprobación
académica requiere cotejar la guía, el SHA final y las evidencias reales.

## Observaciones originales conservadas — histórico previo a commits/PR/CI

La tabla y nota siguientes describen el estado de la reauditoría anterior, no el
estado actual de GitHub. Se conservan para trazabilidad y deben leerse con la
matriz actual y VALIDATION.md.

| Criterio | Estado | Evidencia disponible y cierre necesario |
|---|---|---|
| CE1 (10) | Cumplido en código local | Recursos, variables, data, locals, outputs, dependencias; confirmar parámetros reales |
| CE2 (25) | Parcial | Tres módulos y pruebas; faltan plantilla oficial, plan/apply y portal funcional real |
| CE3 (10) | Parcial | Estructura, ignores y rama correctas; faltan commits autorizados y publicación final |
| CE4 (10) | Pendiente | Guía de commits/PR preparada; no hay PR ni revisión humana ejecutados |
| CE5 (10) | Parcial | CI y candidato con gate/plan; faltan guía institucional, protecciones y ejecución |
| CE6 (10) | Parcial | Reauditoría: 20 regresiones Python aprobadas en cada uno de dos parsers, verificador/TFLint/Checkov/actionlint aprobados; validate/test bloqueados en esta sesión por carga del esquema; falta CI remoto |
| CE7 (10) | Pendiente | Sin autenticación/backend autorizados ni apply desde pipeline |
| CE8 (15) | Parcial | Scripts y protección de archivos preparados; faltan AWS/HTTP/limpieza y entrega inspeccionada |

Los datos sintéticos de pruebas son aislados. Validar/mokear no demuestra despliegue.
Una definición de environment no demuestra gate configurado. Apply no demuestra
portal disponible. Destroy no demuestra limpieza independiente sin consulta AWS.

La corrección del verificador refuerza CE1/CE2 (interpretación y control del ingress),
CE3 (dependencias/pruebas documentadas), CE5/CE6 (CI con ambas variantes del parser)
y la protección de CE8 sin acreditar operaciones AWS. No cambia el estado de
CE4/CE7: no se crearon commits, PR, revisión ni despliegue. Detalles y límites de
las ejecuciones nuevas en la sección de reauditoría de VALIDATION.md.
