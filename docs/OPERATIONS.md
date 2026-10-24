# Operación real pendiente — ejecutar solo con autorización

No se ejecutó plan contra AWS ni apply/destroy. Estas instrucciones son un runbook,
no evidencia de ejecución. AWS CLI debe estar instalado/disponible en la consola
autorizada. No ejecutar `aws configure` con claves inventadas ni publicar su salida.

En Windows, si la política local bloquea `.ps1`, usar para los scripts propios
`powershell.exe -NoProfile -ExecutionPolicy RemoteSigned -File <ruta-del-script>`
con sus argumentos. La opción se limita al proceso; no cambiar políticas globales.
En CI Linux se usa pwsh. No confundir la política de scripts con el error mTLS del
provider documentado en VALIDATION.md: son incidencias diferentes.

## Orden de cierre cuando lleguen los materiales — no ejecutar AWS todavía

Lista confirmada: 8; VPC 172.16.0.0/16 y subnet 172.16.8.0/24. La reutilización
permanece en los inputs; no editar el CIDR de network para otro estudiante.
student_id es obligatorio y debe ser el mismo en nombres y tags; no deducir nombre
legal/RUT a partir del usuario GitHub. Región/tipo de las pruebas son mocks.

| Paso | Acción concreta y condición de avance |
|---|---|
| 1. Plantilla oficial | Obtener user_data_v1.sh.tpl del docente, registrar origen/fecha/SHA256 con Get-FileHash, copiar a templates/ conservando lógica. Revisar variables, SO, paquetes, expansiones shell y alcance de red con templates/README.md. No usar tests/fixtures como bootstrap. |
| 2. Variables | Si no existe lab.auto.tfvars, copiar terraform.tfvars.example; si existe, revisar/completar sin sobrescribirlo. Mantener lista 8; completar student_id real, región/tipo autorizados, AMI/SO compatible y portal_parameters. El archivo incompleto no permite un despliegue. |
| 3. Autenticación | Confirmar cuenta/laboratorio en la guía, incluido si Learner Lab [193444] está autorizado. Implementar mecanismo temporal aprobado en ci/institutional-auth.sh o acción equivalente; comprobar identidad y permisos sin publicar credenciales. No asumir OIDC ni claves permanentes. |
| 4. State | Implementar ci/institutional-init.sh con backend cifrado/acceso mínimo/locking autorizado. Usar el mismo estado en plan/apply/limpieza y init readonly; documentar su ciclo de vida, sin inventar buckets, roles ni IDs. |
| 5. Revisión y activación | Revisar la Draft PR #1 existente, registrar revisión humana y ejecutar CI del SHA final. Integración/activación solo por autorización del responsable y guía. Si se autoriza Actions, configurar environment real, reviewers, ramas, privacidad del plan y adaptar los steps; recién entonces cambiar extensión disabled mediante revisión. |
| 6. Plan y gate | Dispatch autorizado desde main; generar plan binario/texto del SHA exacto, conservar digest/edad, revisar y aprobar en gate efectivo. Si cambia state/código o caduca, crear plan nuevo y aprobarlo nuevamente. |
| 7. Apply automatizado | Aplicar desde pipeline únicamente el plan aprobado, con autenticación nueva del job y backend idéntico. Registrar run ID, SHA, identidad saneada, aprobación y resultado. Nunca por push. |
| 8. Verificación | Ejecutar outputs, consulta AWS del mismo ID/IP, Verify-Deployment.ps1 con región/marcador oficiales y plan posterior. Esperar HTTP 200 con contenido del portal, no solo apply success. Investigar diferencias antes de aceptar. |
| 9. Limpieza | Obtener autorización de destrucción, revisar plan -destroy con gate, aplicar ese plan y ejecutar Verify-Cleanup.ps1 con inventario previo. Confirmar state vacío y ausencia independiente; no borrar state como sustituto del destroy. |
| 10. EVA | Completar 6–8 evidencias reales (plan E01–E08), verificar plantilla oficial de Ficha, identidad y formato. Previsualizar ZIP, revisar secretos/lock/ejemplo y recién construir ZIP/PDF finales; inspeccionar ambos. No generar entregables finales mientras falten evidencias. |

Esta tabla es preparación operativa, no autorización para esos pasos. Conservar
refs de PR/CI base en EVIDENCE.md; la preparación local aún no está en sus checks.

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
