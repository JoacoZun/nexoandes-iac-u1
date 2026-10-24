# Revisión CE1–CE8

Estado al 24-10-2026. No se calculan puntos garantizados: corresponde al docente
evaluar evidencia final y guía institucional completa, que aún no está disponible.

## Matriz actual — preparación lista 8

Pesos de la evaluación, no puntajes obtenidos. Base publicada e7f6025, PR #1 Draft,
dos runs CI success/cuatro checks y cero reviews comprobados por API de solo lectura.
Los cambios locales nuevos NO están acreditados por la CI del commit anterior.

| Criterio/peso | Implementado | Validado realmente | Evidencia disponible | Pendiente y acción concreta |
|---|---|---|---|---|
| CE1 — 10 | Recursos/inputs/outputs/locals/data/dependencias; root default 8 y tag derivado | Base validada en CI; subnet 8 calculada con Terraform console aislado; validación del ajuste según VALIDATION.md | Módulos, E02, commit 86dc894 y jobs controls | Incorporar plantilla/guía y completar región/tipo/identidad; repetir CI del SHA lista 8 |
| CE2 — 25 | Tres módulos reutilizables, X configurable y caso X=255, bootstrap preparado | validate/mocks de base en CI, sin portal AWS probado | E02/E04 y tests; no evidencia funcional AWS | Integrar plantilla original, verificar compatibilidad AMI/tipo, desplegar y demostrar portal; parcial |
| CE3 — 10 | Estructura, ignores, lock y cinco commits coherentes | Git/PR API corroboran historial y 46 archivos de base | E01, log y comparación main...HEAD | Registrar cambios locales solo cuando se autorice y conservar SHA/manifiesto final; base trazable, entrega pendiente |
| CE4 — 10 | Rama feature y Draft PR #1 a main | Existencia/state/head/base comprobados; 0 reviews | E03, URL PR y comparación | Revisión humana real, comentarios/resolución y estado final autorizado; parcial, no aprobado |
| CE5 — 10 | CI activo con permisos mínimos y candidato protegido desactivado | Dos triggers reales; candidate/gate no ejecutados | E04/E05, workflows y PIPELINE.md | Recibir guía; definir auth/state/almacén del plan y configurar gate efectivo antes de activar; parcial |
| CE6 — 10 | Cinco controles y regresiones Python, jobs por parser | Baseline: init/fmt/validate/mocks/TFLint/Checkov/política success en ambos runs; nuevos resultados locales separados | Cuatro checks enlazados en E04 y logs locales | Repetir CI del futuro SHA lista 8; adjuntar logs legibles, no atribuir success previo a código nuevo |
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
