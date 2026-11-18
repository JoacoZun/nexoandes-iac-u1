# Parámetros locales AWS U2: preparación incompleta

`deployment.tfvars` es ignorado por Git y registra exclusivamente los valores
indicados por el usuario: us-east-1, us-east-1a/us-east-1b, AMI
ami-08b275ac6cc5dbefb, t3.micro, /dev/sda1, 8 GiB, base 2 y margen 1.
El módulo ya fija gp3 y cifrado. Resultado de diseño: mínimo/deseado 2,
máximo 3 y límite saludable máximo 150%; no demuestra cuota ni capacidad real.
Portal v1 y refresh deshabilitado quedan explícitos.

## Carga explícita, sin operaciones remotas

Desde el root `u2/aws`, una futura operación autorizada necesita DOS argumentos
de variables: `-var-file=../identity.tfvars` y `-var-file=deployment.tfvars`.
Con `-chdir=u2/aws`, esas rutas también se resuelven desde u2/aws.
Terraform no carga archivos arbitrarios *.tfvars automáticamente ni busca los
del padre: solo terraform.tfvars y *.auto.tfvars tienen carga automática.
La identidad contiene X=8 ratificado por el usuario y c50 (equivalencia asumida
con sección 50); student=a008 se deriva en la composición, no es otro input.

El backend es independiente de esas variables. `backend.hcl` necesita el
argumento explícito `-backend-config=backend.hcl` durante una inicialización
remota futura autorizada; no se carga por existir. No se ha ejecutado esa
inicialización, ni migración, ni plan/apply/destroy. El backend partial conserva
bucket/región/cifrado/locking, pero no key en código versionado.
`init -backend=false` tampoco conecta ni configura el backend remoto.

## Bloqueos deliberados

Faltan account_id, CIDR HTTP autorizados, warmup_seconds, health_grace_seconds,
deregistration_seconds y build_ref real. Se omiten, en lugar de proporcionar
null, cuentas ficticias, CIDR abiertos o tiempos supuestos. El objeto deployment
actual NO satisface el contrato obligatorio completo de variables.tf y no está
listo para una operación. No intentar completar deployment mediante otro
var-file parcial: Terraform sustituye el objeto, no fusiona sus atributos.

`terraform validate` comprueba la configuración, no carga estos var-files ni
demuestra que los parámetros estén completos o sean válidos en AWS. Los tests
mock usan fixtures independientes y tampoco verifican estos destinos reales.

Pendiente sin acceso cloud: confirmar propietario, arquitectura, disponibilidad
y permisos de la AMI en us-east-1; compatibilidad t3.micro y /dev/sda1, tamaño
mínimo del snapshot (8 GiB puede ser insuficiente), cloud-init/systemd/Python,
salida bootstrap, AZ, cuotas para tres instancias y presupuesto. La región del
bucket no demuestra que la región de cómputo esté autorizada por Learner Lab.

State localmente seleccionado: u2/c50/a008/aws/terraform.tfstate, diferente de
fase1/terraform.tfstate y de su lock. Permisos efectivos, propietario del bucket,
versionado y cifrado remoto siguen sin comprobar. Ver BACKEND.md.
No se modifican U1, sus archivos de variables, state ni la plantilla docente.
