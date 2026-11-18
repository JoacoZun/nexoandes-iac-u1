# NexoAndes U2: base local sin cloud

CI exclusiva U2 y validaciones sin cuentas: [CI.md](CI.md).
Azure se entrega como código sin despliegue por autorización docente de S6
informada por el usuario: [alcance y límites](azure/EVALUATION.md).
Azure NO fue desplegado; los resultados mock no son evidencia cloud.
Observación HTTP/controlador, gates y recuperación preparada sin ejecutar: [observation/README.md](observation/README.md).

**Actualización AWS:** el root de contratos de este directorio conserva su carácter
local. El nuevo código de infraestructura está aislado en [`aws/`](aws/README.md),
con provider/lock propios, backend parcial y tests exclusivamente mock. Las notas
de preparación local que siguen se refieren al root `u2/`, no a `u2/aws/`.

Directorio independiente del root U1. No ejecutar comandos U2 desde el root del
repositorio. No se modifican U1, su backend S3, state, lock ni workflows.

Esta etapa implementa contratos Terraform puros y la integración de la plantilla;
NO implementa recursos, autenticación, backend remoto, controlador, despliegue ni
evidencias de ejecución. `contracts` describe intención, no IDs/IP inventados.
No hay providers cargados ni recursos, incluso si `x_ratified` se marca true.

## Material docente e identidad

Copias byte a byte desde Descargas:

- `templates/user_data_u2.sh.tpl`: SHA-256
  `4445eadace792b80ac3e07886d99b80bfd1f250b892731dfc9abda77b9c9e2e3`.
- `templates/README_ESTUDIANTE_U2.md`: SHA-256
  `95a47a6c17e5ae6fe2017b35d4bc674d770351b42118191871ba01e57976262d`.

Una misma plantilla contiene ambas versiones AWS y Azure v1. No se modifica su
lógica. Requiere Linux/cloud-init/Bash/systemd, Python >=3.8, useradd y metadata
autorizada. Puerto 80 libre: nunca superponer el servicio U1. La plantilla usa
biblioteca estándar Python; no requiere nginx ni paquetes pip.

Los defaults conservan `x=8` provisional y `x_ratified=false`. La identidad local
en `identity.tfvars` configura X=8 ratificado por el usuario, a008 derivado y
c50 (equivalencia asumida con sección 50); no se carga automáticamente.
`course` es obligatorio cNN; `student` se deriva de X. `build_ref` es obligatorio y
debe señalar código/artefacto real: el hash no acredita revisión ni despliegue.
Los valores c99/offline-test en tests son fixtures, no datos académicos.

## Composición y contratos

Root comparte identidad y tags, renderiza los seis parámetros oficiales mediante
`templatefile()` y pasa el resultado a módulos locales separados. AWS recibe
`app_version`; Azure fija v1. Los módulos codifican una vez el script a base64 para
futuros Launch Template `user_data` y VM `custom_data`.

| Contexto | Red deseada con X provisional 8 | Próxima composición |
|---|---|---|
| AWS | 10.8.0.0/16; subnets 10.8.10.0/24 y 10.8.20.0/24 | VPC/rutas/IGW, ALB/TG, SG ALB y EC2, Launch Template, ASG |
| Azure | VNet 172.20.8.0/24; subnet 172.20.8.0/26 | RG/VNet/subnet, NSG/NIC, IP pública, VM Linux/disco |

AWS: dos AZ autorizadas; endpoint DNS del ALB; EC2 solo acepta HTTP del SG ALB.
Azure: endpoint IP pública asignada, salida explícita y clave pública administrativa
si la plataforma la requiere, sin abrir SSH. IDs, endpoints y ubicación serán outputs
reales SOLO cuando se implemente y ejecute infraestructura autorizada.

`/health` mide proceso; debe complementarse con `/api/info` y `/api/check` para
identidad, versión, hash, metadata y función. El observador U2 futuro no reutilizará
los reintentos del verificador U1 para ocultar fallos.

## Contextos, providers y estado: diseño pendiente de implementación

Mantener roots de ejecución AWS y Azure separados en la siguiente etapa, con
backend propio, credenciales y permisos acotados. El root local actual NO será el
root de ejecución multi-cloud ni contendrá un state compartido de ambas nubes.

| Contexto | Provider futuro | Ruta lógica de estado propuesta |
|---|---|---|
| AWS | hashicorp/aws; evaluar 6.42.0 existente para el controlador elegido | u2/<course>/<student>/aws/terraform.tfstate |
| Azure | hashicorp/azurerm; versión concreta pendiente de compatibilidad autorizada | u2/<course>/<student>/azure/terraform.tfstate |

No se inventan bucket, cuenta, tenant, suscripción, región ni secrets. No se declaran
providers todavía para que esta base sea totalmente offline. La siguiente etapa
debe fijar versiones verificadas y generar locks independientes para cada root.
Aliases solo si hay configuraciones distintas del MISMO provider. Terraform mínimo
1.10 por el diseño de locking S3 futuro. No usar `fase1/terraform.tfstate`, no migrar
state ni inicializar U1 para trabajar en U2. No hay archivo backend que apunte a U1.

## Verificación sin cloud

Desde el root del repositorio, con Python local disponible:

```powershell
./.tools/python/python.exe -B -m unittest discover -s u2/tests -p 'test_*.py' -v
```

Las pruebas verifican bytes oficiales, configuraciones, tamaño, versiones distintas,
metadata con funciones simuladas y degradación de caché. No ejecutan bootstrap,
servidores, sockets o comandos cloud. La sustitución JSON/base64 Python solo verifica
el contrato; el renderizado Terraform real corresponde a la suite HCL.

Cuando Terraform esté disponible, ejecutar SOLO en `u2/`:

```powershell
terraform fmt -check -recursive
terraform init -backend=false -input=false
terraform validate
terraform test
```

Estos contratos no tienen providers ni recursos cloud. La suite HCL usa `command =
plan` exclusivamente para evaluar expresiones LOCALES, no un plan cloud. No se ha
ejecutado en la preparación si Terraform no está disponible. No ejecutar workflows
U1, plan/apply/destroy cloud ni scripts de operación como parte de estos checks.

## Próximas etapas y riesgos

1. Ratificar X/curso, destinos, cuotas, imágenes y permisos; fijar providers/locks.
2. Implementar roots de ejecución con backends separados y gate real; preservar
   inventarios/diagnósticos antes de limpiar runners (A01). Vincular texto revisado
   al plan (A05), validar cuenta esperada y adaptar política de SG a U2 (A04).
3. Implementar recursos, capacidad base/temporal y un único controlador. Comparar
   rolling/blue-green antes de decidir. No combinar controladores competitivos.
4. Probar v1 en ambas nubes con autorización posterior; luego reemplazo AWS v2 y
   recuperación con protocolo de observación U2 completo y plan posterior.
5. Conservar evidencia real, sanear exportables y verificar limpieza independiente.

La plantilla se acerca al límite AWS de 16 KiB: comprobar script renderizado por
variante antes de codificar exteriormente. AMI/imagen, dependencias del SO y permisos
no están validados en cloud. `x_ratified` es información, no un gate de autorización;
los roots cloud futuros deberán exigir ratificación y contexto aprobado.

No se acreditan CE3/CE5/CE6/CE7 por estos tests. No hay evidencias cloud fabricadas.
Los hallazgos U1 A01–A08 quedan intactos; esta rama no los corrige sobre U1.
Preparación asistida con Codex: integración, contratos y pruebas locales; sin ejecución
cloud ni sustitución de la autoría/revisión exigidas por la evaluación.

## Resultado de preparación local

- 9 pruebas Python offline aprobadas, incluido tamaño con build_ref máximo y guard de mocks AWS.
- 13 archivos HCL parseados sin errores con el parser local disponible.
- `bash -n` sobre la plantilla oficial: exit 0; no ejecuta el bootstrap.
- SHA-256 de ambas copias coincide con Descargas; plantilla coincide además con
  el hash suministrado por el usuario.
- Terraform portátil 1.16.6: fmt/validate y los seis runs HCL locales aprobados.
  La implementación AWS aislada tiene sus propios seis tests mock aprobados;
  consultar `aws/README.md` para distinguirlos de estos contratos locales.
- Ningún archivo U1 versionado modificado; sin operaciones cloud, commit o push.
