## Objetivo y alcance — propuesta local para la PR #1 existente

Convierte la arquitectura Fase 1 de NexoAndes en Terraform modular: VPC
172.16.0.0/16, subnet 172.16.X.0/24, IGW/ruta pública, SG HTTP sin SSH y EC2 con
IP pública, IMDSv2, EBS cifrado y bootstrap parametrizado. Lista confirmada: 8,
subnet 172.16.8.0/24. El root ofrece 8 como default sobrescribible; network sigue
genérico. Región, tipo e identidad deben completarse con datos reales autorizados.

## Cambios

- Módulos network/security/compute, inputs validados, outputs/tags y provider lock
  6.42.0 con checksums Windows/Linux contrastados con HashiCorp.
- `9f4ceac`: default 8, tag ListNumber derivado, prueba root de subnet e identidad
  y ejemplo público de variables sin secretos.
- Integración local posterior de la plantilla docente verificada por SHA-256:
  cinco parámetros explícitos, `student_name` separado de `student_id`, renderizado
  en root y contenido entregado a compute. CI comprueba hash y sintaxis Bash.
- Pruebas con AWS mock, TFLint y Checkov con perfil documentado; CI sin credenciales.
- Candidato de pipeline desactivado con plan guardado, integridad, caducidad,
  concurrencia y gate por environment que requiere configuración manual real.
- Runbooks de verificación AWS/HTTP, limpieza, evidencias y empaquetado limpio.

## Validaciones

Base publicada verificada: `e7f6025bc8fd7e221942c19d3fd0eb579809410b`.
[PR #1](https://github.com/JoacoZun/nexoandes-iac-u1/pull/1) abierta y Draft;
0 revisiones registradas en la consulta del 24-10-2026.

- [Push CI 40106088973](https://github.com/JoacoZun/nexoandes-iac-u1/actions/runs/40106088973): success.
- [PR CI 40106962247](https://github.com/JoacoZun/nexoandes-iac-u1/actions/runs/40106962247): success.
- Cada ejecución tiene controls y repository-python en success: cuatro checks,
  dos ejecuciones; init/format/validate/mocks/lint/security/policy aprobados en la base.

El HEAD local es `9f4ceac`; la integración oficial posterior aún no está cubierta
por esos checks. Repetir CI sobre su futuro SHA antes de revisar integración. Los resultados
locales y el límite mTLS de Codex están en `docs/VALIDATION.md`.
No hay plan real, apply, HTTP ni destroy acreditados. Esta propuesta no se envió a GitHub.

## Riesgos y requisitos pendientes

La plantilla y su README oficial ya están presentes; no modificarlos. Faltan guía
técnica vigente y cotejo de la plantilla de Ficha. La guía debe autorizar región/tipo,
autenticación, backend/locking, gate y laboratorio; Learner Lab [193444] no está
confirmado. Completar `student_id` y `student_name` reales y confirmar compatibilidad
AMI/script. HTTP e IPv4
pública son requisitos y pueden implicar exposición/costo. No activar despliegue
hasta configurar gate, almacenamiento restringido del plan y adaptadores reales.
No contiene recursos adicionales de negocio ni autorización para apply/destroy.

## Revisión solicitada

Cotejar arquitectura, tags/validaciones, pruebas negativas, salida HTTP/HTTPS,
control sin SSH, IMDSv2, protección de state/planes y límites de evidencia.
Adjuntar observaciones humanas reales y resolución antes de merge.
Mantener la PR existente en Draft; esta revisión de Codex no es aprobación humana.
