# Revisión CE1–CE8

Estado local al 24-10-2026. No se calculan puntos garantizados: corresponde al docente
evaluar evidencia final y guía institucional completa, que aún no está disponible.

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
