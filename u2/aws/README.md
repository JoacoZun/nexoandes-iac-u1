# AWS U2: código de infraestructura, sin despliegue

Root independiente: ejecutar cualquier validación desde `u2/aws/`, nunca desde U1.
Reutiliza la composición local `../` y su contrato AWS sin cambiar su interfaz.
Azure sigue siendo un contrato local; no se implementa infraestructura Azure aquí.

## Archivos y composición

- `versions.tf`: Terraform >=1.16.6, AWS exactamente 6.42.0 y backend S3 parcial.
- `variables.tf`: identidad compartida y objeto obligatorio `deployment`.
- `main.tf`: contexto AWS con cuenta permitida y módulos composition/infrastructure.
- `modules/infrastructure/network.tf`: VPC `10.X.0.0/16`, subredes
  `10.X.10.0/24` y `10.X.20.0/24`, dos AZ distintas, IGW/ruta/asociaciones.
- `security.tf`: SG ALB y EC2 separados; entrada ALB desde CIDR autorizados,
  EC2 solo desde SG ALB; egreso ALB a EC2 TCP/80 y bootstrap TCP/80/443.
- `service.tf`: ALB HTTP público, listener y Target Group con drenaje configurable.
- `compute.tf`: Launch Template con IMDSv2 obligatorio, hop 1, EBS gp3 cifrado,
  tags de instancia/volumen/NIC y bootstrap base64 recibido del contrato.
- ASG: min=desired=base; max=base+margen; sin políticas de autoescalamiento dinámico.
- `outputs.tf`: endpoint ALB, IDs y controlador separados. No inventa IDs EC2 ni
  IDs/resultados de Instance Refresh; estos requieren consultas del proveedor.

La plantilla docente `../templates/user_data_u2.sh.tpl` no se modifica. SHA-256:
`4445eadace792b80ac3e07886d99b80bfd1f250b892731dfc9abda77b9c9e2e3`.
El contrato usa `templatefile()` y codifica una vez. Se verifica el tamaño del
bootstrap por bytes base64 antes del límite EC2 de 16 KiB.

## Parámetros reales pendientes

Preparación local actual: ver `LOCAL_PARAMETERS.md` y el archivo ignorado
`deployment.tfvars`. Los valores indicados por el usuario no se han verificado
en AWS; el objeto permanece incompleto y requiere carga explícita junto con
la identidad, independientemente de `backend.hcl`.

Los defaults mantienen X=8 provisional y `x_ratified=false`. La configuración
local explícita `../identity.tfvars` ratifica X=8 por instrucción del usuario y
usa c50 (sección 50, equivalencia asumida); ver `../IDENTITY.md`.
Course y build no tienen valores reales predeterminados.
`deployment` exige cuenta, región, dos AZ, AMI, tipo, nombre de dispositivo raíz,
tamaño del disco, capacidad base/margen, CIDR HTTP y tiempos de warmup/gracia/drenaje.
Verificar tamaño mínimo del snapshot raíz, arquitectura y cloud-init/systemd/Python
de la AMI. No se consulta `most_recent` ni se inventa una imagen.

Se conserva capacidad saludable del 100%; margen >=1 y <=base. El porcentaje máximo
se deriva de base+margen, hasta 200%, sin asumir cuota disponible. Los porcentajes
tienen granularidad entera: seleccionar una combinación representable. Capacidad
base 1 es válida pero no acredita tolerancia a fallos entre AZ. Definir la capacidad
real tras revisar presupuesto, cuota y requisitos de continuidad.

EC2 solicita IPv4 pública únicamente para bootstrap por IGW en esta referencia;
el SG no permite HTTP directo. No se crean NAT Gateway, SSH, roles IAM ni claves.
Confirmar permisos/service-linked role de Auto Scaling en el laboratorio.

## Rolling preparado, no iniciado

`enable_instance_refresh=false` por defecto: no existe bloque activo de refresh.
La versión de Launch Template del ASG se referencia por número concreto,
no `$Latest` ni `$Default`. Al habilitar el flag EN UNA OPERACIÓN FUTURA AUTORIZADA,
un cambio de Launch Template puede iniciar Instance Refresh mediante el provider.
No habilitarlo con un refresh en curso ni iniciar otro controlador paralelo.

Preferencias: Rolling, mínimo saludable 100%, máximo derivado del margen,
warmup configurable, skip_matching=true; instancias protegidas/standby esperan.
No se promete rollback automático: `auto_rollback=false`. Conservar la referencia
v1 (AMI/build y LT numérica) para recuperación por otra operación controlada.

El provider 6.42.0 NO espera que termine el refresh. Un pipeline futuro debe esperar
y consultar el controlador hasta resultado terminal, salud de todos los destinos,
versión/función y capacidad; `apply success` no acredita la actualización. Deshabilitar
el flag tampoco cancela por sí solo una operación ya iniciada.

La ruta TG `/health` solo acredita proceso. Complementar con `/api/info` y
`/api/check`, versión/build/backend y protocolo U2 completo: HTTP cada 2 s,
timeout 5 s sin reintentos ocultos, desde -60 s hasta estabilización +120 s;
capacidad/controlador cada <=30 s. No hay observador ni recuperación ejecutados.

## Protección del state

Backend parcial S3 con cifrado/locking, bucket `nexoandes-tfstate-est8-1793333880`
y región `us-east-1` solicitados; key omitida del bloque versionado y resuelta
localmente en `backend.hcl` como `u2/c50/a008/aws/terraform.tfstate`. Ver
`BACKEND.md` para parametrización segura, permisos y verificaciones pendientes. La key
esperada es `u2/<course>/<student>/aws/terraform.tfstate`, visible en `context`.
Configurar almacenamiento autorizado y esa key al incorporar pipeline; no usar
`fase1/terraform.tfstate`, backend de U1 ni migrar/copiar su state. Validar cuenta,
key, versionado, política y lifecycle antes de cualquier operación cloud futura.
Los backends no admiten variables: el output informa la key, no configura el backend.

`.terraform.lock.hcl` es una copia independiente del lock existente (6.42.0), usado
readonly al inicializar desde el provider local con checksums del lock. No se tocó
el lock de U1. En otro SO, verificar hashes/firmas y disponibilidad del paquete.

## Validaciones offline

`init -backend=false` se utiliza solo para registrar módulos/provider local; no
inicializa S3. `validate` no consulta la cuenta. Los seis runs de `tests/` usan
`mock_provider "aws" { override_during = plan }` y `command = plan`, sin apply.
Sus cuenta, región, AZ, AMI, tipo y CIDR son fixtures sintéticas, no configuración
autorizada ni evidencia. No ejecutar un plan CLI real para probar estos tests.

La base `u2/` conserva seis tests locales y las pruebas Python de la plantilla.
El contrato puro y las pruebas AWS mock se validan por separado. No usar
`scripts/Invoke-Checks.ps1` de U1 como runner de esta infraestructura.

## Costos y pendientes

Una ejecución autorizada futura puede cobrar ALB/LCU, EC2 base y temporal, EBS,
IPv4 públicas, transferencia y S3 state/evidencias. No se asume Free Tier ni se
generó estimación con datos inventados. Esta implementación no genera esos cargos.

Pendiente: ratificación de identidad, imágenes/destinos/cuotas, backend real,
review/gate/pipeline, retención de evidencias, observación y espera del controlador,
ensayos v1→v2/recuperación y limpieza independiente. No se acredita CE3/CE5/CE6/CE7.

Referencias técnicas del provider fijado:
- [ASG / Instance Refresh 6.42.0](https://github.com/hashicorp/terraform-provider-aws/blob/v6.42.0/website/docs/r/autoscaling_group.html.markdown)
- [Launch Template 6.42.0](https://github.com/hashicorp/terraform-provider-aws/blob/v6.42.0/website/docs/r/launch_template.html.markdown)
- [Terraform provider mocking](https://developer.hashicorp.com/terraform/language/tests/mocking)

Implementación asistida con Codex para código y tests offline, sin operación cloud.

## Validación de esta implementación

- Terraform 1.16.6: `fmt -check -diff -recursive` en U2, PASS.
- AWS `init -backend=false -input=false -lockfile=readonly` con provider de la
  caché local existente: PASS; no inicializó backend S3 ni autenticó AWS.
- `validate` de AWS y base local: PASS.
- AWS mock: 6 passed, 0 failed. Antes de ejecutar se comprobó que ambos archivos
  declaran mock_provider AWS, solo command=plan y sin overrides de provider real.
- Contratos locales de U2: 6 passed, 0 failed.
- Python: 9 pruebas aprobadas; incluye integridad docente, tamaño, metadata simulada
  y guard de seguridad para la suite mock AWS.
- Hash docente intacto y diff de archivos U1 versionados vacío.

Los primeros intentos de tests detectaron fixtures de ID LT inválido y referencias
de SG desconocidas durante plan; se corrigieron solo los mocks con IDs sintéticos
y overrides durante plan. No se cambió a apply ni se debilitó la comprobación de SG.
Estos resultados verifican código y contratos, no comportamiento/continuidad AWS.
