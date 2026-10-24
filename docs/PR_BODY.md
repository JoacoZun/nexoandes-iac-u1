## Objetivo y alcance

Convierte la arquitectura Fase 1 de NexoAndes en Terraform modular: VPC
172.16.0.0/16, subnet 172.16.X.0/24, IGW/ruta pública, SG HTTP sin SSH y EC2 con
IP pública, IMDSv2, EBS cifrado y bootstrap parametrizado. X/región/tipo/estudiante
se proporcionan explícitamente; no se despliega con valores asumidos.

## Cambios

- Módulos network/security/compute, inputs validados, outputs/tags y provider lock.
- Integración de plantilla docente con bloqueo si falta o no se puede renderizar.
- Pruebas con AWS mock, TFLint y Checkov con perfil documentado; CI sin credenciales.
- Candidato de pipeline desactivado con plan guardado, integridad, caducidad,
  concurrencia y gate por environment que requiere configuración manual real.
- Runbooks de verificación AWS/HTTP, limpieza, evidencias y empaquetado limpio.

## Validaciones

Ver resultados y límites en `docs/VALIDATION.md`. Son validaciones locales;
no hay ejecución de GitHub Actions, plan real, apply, HTTP ni destroy acreditados.
Actualizar aquí el SHA/run ID cuando existan; no atribuir CI remoto a logs locales.

## Riesgos y requisitos pendientes

Faltan número de lista, región/tipo EC2 autorizados, plantilla oficial, guía de
CI/CD, autenticación y backend. Confirmar compatibilidad AMI/script. HTTP e IPv4
pública son requisitos y pueden implicar exposición/costo. No activar despliegue
hasta configurar gate, almacenamiento restringido del plan y adaptadores reales.
No contiene recursos adicionales de negocio ni autorización para apply/destroy.

## Revisión solicitada

Cotejar arquitectura, tags/validaciones, pruebas negativas, salida HTTP/HTTPS,
control sin SSH, IMDSv2, protección de state/planes y límites de evidencia.
Adjuntar observaciones humanas reales y resolución antes de merge.
