# Operación real pendiente — ejecutar solo con autorización

No se ejecutó plan contra AWS ni apply/destroy. Estas instrucciones son un runbook,
no evidencia de ejecución. AWS CLI debe estar instalado/disponible en la consola
autorizada. No ejecutar `aws configure` con claves inventadas ni publicar su salida.

En Windows, si la política local bloquea `.ps1`, usar para los scripts propios
`powershell.exe -NoProfile -ExecutionPolicy RemoteSigned -File <ruta-del-script>`
con sus argumentos. La opción se limita al proceso; no cambiar políticas globales.
En CI Linux se usa pwsh. No confundir la política de scripts con el error mTLS del
provider documentado en VALIDATION.md: son incidencias diferentes.

## Preparación

1. Completar requisitos pendientes del README y revisar plantilla original/SHA256.
2. Ejecutar cinco controles sin AWS; resolver fallos. Confirmar PR, SHA revisado y
   estrategia institucional de CI/CD, credenciales y state. No guardar secretos
   en TF_VAR, tfvars versionados, user_data, logs o PR.
3. Autenticarse mediante mecanismo temporal autorizado y revisar
   `aws sts get-caller-identity --region <region-real>`; guardar evidencia saneada.
4. Configurar backend autorizado y `terraform init -input=false -lockfile=readonly`.
   Revisar con cuidado cualquier migración de state; no usar `-force-copy` ni
   `force-unlock` rutinariamente. No crear segundo state para recursos existentes.
5. Activar pipeline solo después de los controles de docs/PIPELINE.md y autorización.

## Plan, gate, apply y verificación

El pipeline debe guardar plan y texto del SHA exacto; revisar alcance/costo y aprobar
mediante gate protegido. Apply recibe el plan binario aprobado, no variables nuevas.
Conservar salida de ejecución, identidad temporal saneada, backend y locking (sin
secretos), hash del plan, aprobador y run ID. No considerar apply como prueba HTTP.

Después del apply, en el contexto del mismo backend/commit/credenciales:

```powershell
terraform output
terraform output -json
# Consultar ID real del output; no sustituir por una instancia ajena.
aws ec2 describe-instances --instance-ids <instance-id-real> --region <region-real> --output json
curl.exe --fail --show-error --max-time 15 http://<ip-real>/
./scripts/Verify-Deployment.ps1 -Region <region-real> -PortalMarker '<texto-real-de-la-plantilla>'
terraform plan -input=false -detailed-exitcode -lock-timeout=120s
```

En Linux usar `curl`, no `curl.exe`. El script exige HTTP 200 y marcador oficial,
reintenta el arranque y coteja ID/IP/VPC/subnet/SG/IMDSv2 con AWS. Guarda inventario
con IDs y hash del cuerpo en `artifacts/verification/`; conservarlo de forma protegida
antes de destroy. El marcador se define tras inspeccionar la plantilla real.
Un 200 de un servidor arbitrario no basta para identificar el portal oficial.

Plan posterior: 0 = sin cambios; 1 = error; 2 = cambios. Con 2 investigar y explicar
antes de registrar éxito (p. ej., cambio de AMI `most_recent` o edición externa).
No aplicar automáticamente cambios de deriva. Un fallo HTTP requiere revisar estado
EC2/status checks, rutas, SG y salida de consola/cloud-init por método autorizado;
no abrir SSH como atajo. Los logs pueden contener datos sensibles y se deben sanear.

## Limpieza controlada

Obtener autorización explícita e independiente para destruir. Conservar inventario,
SHA y state seguro; usar el mismo backend/cuenta/región. El siguiente flujo es solo
un procedimiento que debe integrarse con el gate institucional antes de ejecutarse:

```powershell
terraform plan -destroy -input=false -lock-timeout=120s -out=cleanup.tfplan
terraform show -no-color cleanup.tfplan
# Revisar recursos exactos, hash y autorización; no aplicar si el plan cambió.
Get-FileHash cleanup.tfplan -Algorithm SHA256
# SOLO tras aprobación explícita del plan anterior:
terraform apply -input=false -lock-timeout=120s cleanup.tfplan
./scripts/Verify-Cleanup.ps1 -InventoryPath artifacts/verification/inventory.json
terraform state list
terraform plan -destroy -input=false -detailed-exitcode
```

Un plan normal después de destroy propondrá reconstruir recursos: es esperado.
Para demostrar ausencia de recursos gestionados, state vacío y plan `-destroy`
sin cambios, junto a consultas AWS independientes, son más apropiados.
El script de limpieza admite EC2 `terminated` (puede seguir visible temporalmente),
pero exige ausencia de VPC, subnet, SG y EBS raíz mediante filtros de los IDs guardados.
Reintentar consultas solo por consistencia eventual; no interpretar error de permisos,
región incorrecta o fallo CLI como recurso ausente. Revisar también IGW/route table
y recursos por tags Project/Student si hubo interrupciones. El backend no forma
parte del destroy del proyecto salvo instrucción separada.

Retener evidencia saneada y state según política; no borrar state para aparentar
limpieza. No incluir planes ni inventarios crudos en ZIP/PDF. Registrar incidencias,
correcciones y resultado independiente de cada etapa con fecha y SHA.
