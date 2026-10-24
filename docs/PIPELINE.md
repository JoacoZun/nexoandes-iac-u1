# CI/CD candidato y condiciones de activación

`ci.yml` solo comprueba código; no ejecuta plan/apply/destroy ni recibe credenciales.
Se dispara por PR a main, push a feature/fase1-iac, dispatch manual o workflow_call.
La plataforma institucional sigue pendiente: GitHub Actions es una propuesta
revisable, no una autorización. Adaptar el diseño si la guía requiere otra.

`deploy.yml.disabled` no es un workflow activo. Además los dos adaptadores `ci/`
terminan con error explícito. No basta con renombrar el archivo para desplegar.

Estado comprobado al 24-10-2026: CI de e7f6025 pasó para push
[40106088973](https://github.com/JoacoZun/nexoandes-iac-u1/actions/runs/40106088973)
y PR [40106962247](https://github.com/JoacoZun/nexoandes-iac-u1/actions/runs/40106962247),
con controls y repository-python aprobados en cada ejecución. No se cambian
triggers ni permisos: contents:read, sin id-token/credenciales ni plan/apply en CI.
Terraform 1.16.6, provider 6.42.0, acciones por SHA, TFLint/plugin y dependencias
directas Python están fijados. Las dependencias transitivas pip no son un lock
hermético. El init Linux readonly pasó en ambos jobs controls; los SHA256 zh de
Linux/Windows también se cotejaron con el manifiesto oficial de HashiCorp.
El cambio local lista 8 requiere su propia corrida futura de CI.

Flujo candidato: dispatch desde main → cinco controles → autenticación temporal
e init con backend aprobado → plan binario y texto del mismo SHA → artefacto
inmutable de la misma ejecución → environment con required reviewers → verificación
de hash/SHA/edad → apply del plan guardado → AWS/HTTP → plan sin cambios → evidencia.
No hay apply en pushes. Un plan caduca a las cuatro horas; iniciar ejecución nueva
para volver a planificar y aprobar. No se permiten reruns de una ejecución aprobada.
Si hay deriva/state alterado o plan obsoleto, fallar y generar nuevo plan, nunca
regenerarlo silenciosamente en apply. Terraform valida linaje/serial del state.

## Configuración manual requerida antes de habilitar

1. Recibir guía y autorización expresa para plataforma, cuenta, región, tipo EC2,
   plantilla oficial, método de autenticación, backend y despliegue.
2. Incorporar plantilla real revisada, variables completas y un marcador de contenido
   oficial para `PORTAL_EXPECTED_MARKER`. Pasar las variables no secretas mediante
   configuración aprobada/TF_VAR; no interpretar contenido externo como código shell.
3. Reemplazar `ci/institutional-auth.sh` por autenticación temporal aprobada, ejecutada
   de nuevo en cada job. Si se permite OIDC, restringir trust a repositorio, branch o
   environment exactos y audience; usar roles separados plan/lectura y apply mínimo.
   No se han inventado roles, cuentas ni políticas IAM funcionales. El permiso
   `id-token: write` del candidato no configura por sí mismo confianza ni credenciales.
   Un `export` dentro del step que hace source no sobrevive automáticamente a los
   siguientes steps de Actions. La integración autorizada deberá proporcionar
   credenciales temporales al job (acción institucional o mecanismo aprobado para
   GITHUB_ENV, sin secretos en logs), además de estar disponibles al init del mismo
   step. Autenticar cada job por separado; no transferir credenciales en el artefacto
   del plan. Nada de esto se configura definitivamente antes de recibir la guía.
4. Reemplazar `ci/institutional-init.sh`: materializar backend autorizado e inicializar
   **el mismo** estado remoto, cifrado y con locking en plan/apply. Usar
   `-lockfile=readonly`, restringir acceso al state y verificar cuenta/identidad mediante
   `aws sts get-caller-identity`. No guardar secretos en backend versionado ni artefactos.
   Si se autoriza S3, valorar `use_lockfile` con Terraform compatible; no crear S3,
   DynamoDB ni otro backend sin instrucción institucional. Separar su ciclo de vida.
5. Crear environment EXACTO `nexoandes-lab-approved` **antes** de activar; exigir
   required reviewers, impedir autoaprobación, deshabilitar bypass de administradores
   y limitar despliegue a main. Confirmar que plan/visibilidad de GitHub soporta reglas.
   Un nombre de environment sin protecciones no constituye un gate. Guardar captura
   verificable de configuración; si la cuenta no soporta gate, usar mecanismo
   institucional equivalente y adaptar workflow. No activar con protecciones ausentes.
6. Proteger main con PR/revisión independiente y controles obligatorios. Revisar
   cambios a workflows, adaptadores, tests, backend y lock como código privilegiado.
   Restringir quién puede dispatch/aprobar y acceso a artefactos. Usar `actionlint`
   para validación semántica adicional del candidato antes de activarlo.
7. **Resolver privacidad de planes antes de upload**: en repos públicos los artefactos
   pueden ser accesibles a usuarios con acceso de lectura. Un plan binario puede
   contener información sensible incluso cuando el texto la oculta. El upload del
   candidato requiere almacenamiento de acceso restringido aprobado (o repos privado
   autorizado con controles adecuados). Si no existe, sustituir upload/download por
   mecanismo institucional protegido; nunca subir planes sensibles a un repos público.
8. Verificar retención, hashes y permiso del almacén; luego renombrar el candidato a
   `.yml` mediante PR revisada. La activación no autoriza por sí sola un dispatch.

La guía debe confirmar además si AWS Academy Learner Lab [193444] es el laboratorio
válido y si sus restricciones permiten el mecanismo propuesto. No usar ese número
como account ID/rol AWS ni asumir que permite crear IAM u OIDC. Siguen pendientes
región, tipo EC2, identidad académica real, cuenta/roles o sesión temporal autorizada,
ubicación/cifrado del state, locking, gate y privacidad del plan. El candidato sigue
disabled y los adaptadores siguen fallando explícitamente.

El hash SHA256 esperado pasa por outputs del job plan, separado del archivo descargado;
el job apply compara hash, commit y antigüedad. El nombre de artefacto incluye run ID
y SHA; download no busca un artefacto de otra ejecución. El mismo Terraform y provider
lock se usan en ambos jobs. La concurrencia global evita solapar ejecuciones de este
workflow, incluso mientras espera aprobación. El backend lock sigue siendo necesario:
la concurrencia de Actions no coordina operaciones locales u otros workflows.

El revisor debe abrir `review.txt`, cotejar SHA/digest y alcance de recursos, confirmar
que no hay SSH ni reemplazos/costos inesperados y aprobar en el environment. Registrar
run ID, aprobador, fecha y hash. Si se cambia configuración/código/state, se requiere
plan y aprobación nuevos. Los artefactos del candidato duran un día, pero la validez
del plan es de cuatro horas. Exportar evidencia saneada antes de vencer retención.

La destrucción es un procedimiento separado y autorizado: plan `-destroy`, revisión
y gate equivalentes, apply del plan de destrucción aprobado y consulta independiente.
No se incluye botón de destroy habilitado ni ejecución automática.

Fuentes: [GitHub environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments),
[HashiCorp saved plans](https://developer.hashicorp.com/terraform/cli/commands/plan).
