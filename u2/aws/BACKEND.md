# Backend AWS U2: preparación local, sin inicialización remota

Destino solicitado: bucket `nexoandes-tfstate-est8-1793333880`, región
`us-east-1`. Se reutiliza almacenamiento, nunca el objeto state de U1.
`versions.tf` conserva `encrypt=true` y `use_lockfile=true`.
No se verificaron existencia, propietario, permisos ni configuración del bucket.

## Configuración local resuelta

Por instrucción del usuario: X=8 ratificado, student=a008 derivado y course=c50
(equivalencia asumida con sección 50, no confirmación documental docente).
`../identity.tfvars` contiene esos inputs; no se carga automáticamente.
`backend.hcl` contiene bucket, región, key `u2/c50/a008/aws/terraform.tfstate`,
`encrypt=true` y `use_lockfile=true`. Ambos archivos están ignorados por Git.
El bloque backend de `versions.tf` sigue parcial; nada se ha inicializado
remotamente. Ver `../IDENTITY.md` para consumir la identidad explícitamente.

## Regla de parametrización para otros contextos

La key se omite del bloque versionado. Para cambiar de identidad antes de una
inicialización futura autorizada:

1. Ratificar X entero entre 1 y 254 y curso real con formato `cNN`.
2. Derivar student con `format("a%03d", X)` usando el mismo X del root AWS.
3. Derivar la key mediante `u2/` + curso + `/` + student +
   `/aws/terraform.tfstate`. Esta fórmula es documentación, no una key real.
4. Revisar coincidencia exacta con `context.expected_state_key`; el output no
   configura ni restringe el backend. No se puede usar una variable Terraform
   dentro del bloque backend.
5. Solo después, preparar `u2/aws/backend.hcl` con el destino resuelto y las
   opciones de cifrado/locking. Ese nombre está ignorado. Nunca incluir credenciales.
   La inicialización remota requiere autorización independiente; este cambio
   no la ejecuta ni la autoriza. Usar modo no interactivo en el futuro para
   evitar introducir una key manualmente por error.

Trabajar exclusivamente desde `u2/aws`, con workspace `default`; otros
workspaces alteran la ruta efectiva. No reutilizar `.terraform` de U1 ni pasar
su configuración de backend. No migrar ni copiar state. La metadata existente
de validaciones offline tampoco demuestra un backend remoto configurado.

## Aislamiento de U1 y permisos mínimos previstos

U1 utiliza `fase1/terraform.tfstate` en el mismo bucket. La key U2 y su lock
deben ser objetos diferentes. La separación por key no constituye una barrera
IAM si las credenciales permiten acceso amplio al bucket.

Después de resolver la key real, revisar una política limitada a:

- `s3:ListBucket` sobre `arn:aws:s3:::nexoandes-tfstate-est8-1793333880`,
  con condición de prefijo ajustada a la ruta U2 necesaria.
- `s3:GetObject` y `s3:PutObject` sobre el ARN del objeto state U2 exacto.
- `s3:GetObject`, `s3:PutObject` y `s3:DeleteObject` sobre ese mismo ARN
  con sufijo `.tflock` para adquirir y liberar el bloqueo.
- No se requiere `s3:DeleteObject` sobre el state, ni permisos DynamoDB.
  Estos permisos no deben conceder acceso a `fase1/terraform.tfstate` ni a
  su `.tflock`; revisar también permisos heredados y políticas del bucket.

No se genera una política aplicable con ARN incompleto ni comodines de alumno.
Si el bucket exige una clave KMS administrada por el cliente, revisar también
la key policy y permisos KMS de cifrado/descifrado/generación de claves.
`encrypt=true` por sí solo no verifica esa política, versionado ni bloqueo de
acceso público. Confirmar propietario/cuenta del backend por separado:
`allowed_account_ids` del provider AWS no protege el backend S3.

Referencia: https://developer.hashicorp.com/terraform/language/backend/s3

## Pendientes antes de conectar

- Confirmar documentalmente la equivalencia sección 50 = c50 antes de publicar evidencias.
- Revisar permisos sobre el ARN exacto del state y su lock:
  `arn:aws:s3:::nexoandes-tfstate-est8-1793333880/u2/c50/a008/aws/terraform.tfstate`
  y el mismo ARN con sufijo `.tflock`.
- Confirmar propietario, región real, versionado, cifrado y políticas del bucket.
- Confirmar permisos efectivos con credenciales temporales autorizadas de
  Learner Lab, sin almacenarlas en archivos ni en Git.
- Incorporar controles de destino en el futuro pipeline U2; nunca ejecutar
  el workflow de despliegue U1 para este root.
