# Pipeline AWS Academy candidato — desactivado

Estado revisado el 30-10-2026. `.github/workflows/deploy.yml.disabled` permanece
inerte: GitHub no ejecuta esa extensión. `ci.yml` se conserva intacto y sigue siendo
la etapa reutilizable de validación. No se ejecutaron operaciones AWS desde esta
preparación.

El backend versionado usa S3 con cifrado y bloqueo nativo:

- bucket: `nexoandes-tfstate-est8-1793333880`;
- key: `fase1/terraform.tfstate`;
- región: `us-east-1`;
- `encrypt = true` y `use_lockfile = true`.

El plan real informado previamente fue `11 to add, 0 to change, 0 to destroy`.
Ese resultado es antecedente; el workflow debe generar, proteger y aprobar su propio
plan del SHA ejecutado. No reutiliza un plan local ni simula una aprobación.

## Flujo preparado

1. `controls` llama al workflow CI aprobado.
2. `plan`, únicamente desde `main` y en el primer intento, valida credenciales
   temporales, bloqueo público del bucket e inicializa el backend existente.
3. Terraform genera un plan binario sin imprimirlo en logs. El binario, su texto de
   revisión y un manifiesto se almacenan con SSE-S3 bajo
   `fase1/plans/<run-id>/<commit>/`.
4. El resumen de GitHub muestra solo commit y conteos add/change/destroy. El revisor
   debe abrir `review.txt` desde S3 con acceso autorizado antes de aprobar.
5. El job `apply` referencia el Environment `nexoandes-lab-approved`. Sus reglas de
   required reviewers constituyen el gate real; el nombre YAML por sí solo no basta.
6. Después del gate se vuelve a autenticar, se descarga el mismo plan y se comprueban
   SHA-256, manifiesto, commit, cuenta AWS y antigüedad máxima de 45 minutos.
7. Se inicializa el mismo backend y se aplica exclusivamente el plan guardado.
8. `Verify-Deployment.ps1` correlaciona outputs, AWS, IMDSv2 e HTTP. Un plan posterior
   debe devolver exit 0; exit 2 se trata como deriva y falla el job.
9. El workflow intenta retirar los objetos de plan y diagnósticos locales incluso si
   falla. Una lifecycle rule S3 es necesaria para ejecuciones canceladas o no aprobadas.

No hay `id-token: write`, roles OIDC, access keys permanentes ni `terraform.tfvars`.
Los adaptadores `ci/institutional-auth.sh` e `institutional-init.sh` continúan
bloqueados y ya no son invocados por este candidato.

## Secrets y variables requeridos

El job plan requiere GitHub Repository Secrets actuales:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_SESSION_TOKEN`
- `TF_VAR_STUDENT_ID`
- `TF_VAR_STUDENT_NAME`

El Environment protegido debe definir nuevamente los mismos Secrets para `apply`.
Los Secrets del Environment se entregan solo después de la aprobación y pueden
actualizarse antes de aprobar si la sesión Academy cambió. Nunca imprimirlos, pasarlos
por outputs ni guardarlos en S3.

El workflow fija como variables no secretas: lista `8`, región `us-east-1`, tipo
`t3.micro` y marcador oficial del portal. Terraform recibe todo mediante `TF_VAR_*`;
no lee ni publica `terraform.tfvars`.

## Bloqueos antes de activar

No renombrar el archivo hasta comprobar todos estos puntos:

1. Crear `nexoandes-lab-approved`, exigir al menos un revisor humano distinto del
   ejecutor, limitar despliegues a `main` y deshabilitar bypass administrativo.
2. Confirmar que el plan job puede usar los Repository Secrets y que el apply job
   recibe los Environment Secrets protegidos. Las tres credenciales deben pertenecer
   a la misma sesión temporal y estar vigentes durante su job.
3. Confirmar que ambas identidades corresponden a la misma cuenta AWS. Si las
   credenciales vencen o el gate supera 45 minutos, actualizar Secrets e iniciar una
   ejecución nueva; no usar rerun sobre un plan anterior.
4. Verificar permisos mínimos efectivos para STS, EC2/VPC y S3 backend, incluidos
   `GetObject`, `PutObject` y `DeleteObject` en `fase1/plans/*`, objetos de state/lock
   y lectura de Public Access Block. Learner Lab puede restringir estas acciones.
5. Confirmar las cuatro opciones de S3 Block Public Access. Configurar una lifecycle
   rule que elimine `fase1/plans/` en un máximo de un día. El workflow no altera la
   configuración del bucket.
6. Asegurar que solo revisores autorizados puedan leer el texto del plan protegido.
   No subir plan, state, logs completos ni inventario AWS como GitHub artifacts.
7. Ejecutar `actionlint` y revisión humana del diff final. Después, activar mediante
   PR revisada y realizar un nuevo dispatch autorizado desde `main`.

La configuración del Environment, sus reviewers, Secrets, políticas S3 y permisos
Academy no puede garantizarse desde este archivo desactivado. Hasta comprobarlos,
el pipeline es diseño preparado y no evidencia CE7 de despliegue efectivo.
