# Portal Operacional NexoAndes V1 — guía para estudiantes

## ¿Qué se entrega?

El archivo `user_data_v1.sh.tpl` es una plantilla de inicio para una instancia EC2. Instala nginx y publica el Portal Operacional V1. Su programación interna ya está preparada: tu tarea en la Unidad 1 es **integrarla, parametrizarla, desplegarla y verificarla** con Terraform y el flujo de automatización solicitado en la evaluación.

**Sobre `t2.micro` en la vista previa:** es el valor predeterminado del repositorio formativo `lab-red-aula-iac`, usado aquí solo como ejemplo. La evaluación, la rúbrica y el diagrama final de Fase 1 no fijan un tipo EC2 específico. Usa el tipo permitido por la guía vigente y por tu entorno de laboratorio. En el despliegue real, la plantilla obtiene el tipo mediante IMDSv2 y muestra el valor que AWS entregue.

El repositorio formativo es un apoyo para estudiar módulos, red, EC2 y `user_data`; no es la solución final de NexoAndes. Allí la red de ejemplo es `10.20.0.0/16`, el bootstrap usa Apache y se lee con `file()`. Para la evaluación debes seguir el HLD final (`172.16.0.0/16` y subnet `172.16.X.0/24`, con `X` igual a tu número de lista) e integrar esta plantilla con `templatefile()`.

## 1. Coloca la plantilla en tu proyecto

Una organización posible es:

```text
terraform/
├── main.tf
├── variables.tf
├── outputs.tf
├── modules/
│   ├── network/
│   └── compute/
└── templates/
    └── user_data_v1.sh.tpl
```

Puedes usar otra estructura modular si cumple la evaluación. Conserva el contenido de la plantilla sin alterar su lógica, HTML ni CSS.

## 2. Entrega estos cinco valores desde Terraform

| Clave de `templatefile()` | Qué representa | Ejemplo |
|---|---|---|
| `student_name` | Nombre del estudiante | `Camila Rojas` |
| `student_number` | Número de lista del estudiante | `17` |
| `environment` | Ambiente de la fase | `fase1` |
| `portal_version` | Versión visible | `v1` |
| `project_name` | Nombre del proyecto | `NexoAndes Portal Operacional` |

Usa valores de identificación simples y sin secretos. En el HLD final, `student_number` también determina `X` en la subnet `172.16.X.0/24`; para ese uso debe ser un número válido entre 1 y 254.

Ejemplo en el módulo raíz, suponiendo que la carpeta `templates` está junto a `main.tf`:

```hcl
variable "student_name" {
  type = string
}

variable "student_number" {
  type = number
}

locals {
  portal_user_data = templatefile(
    "${path.module}/templates/user_data_v1.sh.tpl",
    {
      student_name   = var.student_name
      student_number = tostring(var.student_number)
      environment    = "fase1"
      portal_version = "v1"
      project_name   = "NexoAndes Portal Operacional"
    }
  )
}
```

Pasa `local.portal_user_data` al recurso EC2 o como variable de entrada de tu módulo de cómputo. En el recurso EC2, la parte relevante es:

```hcl
resource "aws_instance" "portal" {
  # Completa AMI, tipo, subnet, Security Group y tags según tu arquitectura.

  user_data                   = local.portal_user_data
  user_data_replace_on_change = true

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }
}
```

Si `aws_instance` está dentro de un módulo, pasa el contenido como entrada y asigna allí `user_data = var.portal_user_data`. Ajusta la referencia `path.module` a la ubicación real de tu plantilla.

Las secuencias `$${...}` dentro de `user_data_v1.sh.tpl` son intencionales: permiten que Terraform deje variables para Bash. No las cambies.

## 3. Despliega con el flujo exigido

Versiona el código y realiza la revisión de cambios y el pipeline indicados en la evaluación. El pipeline debe dejar evidencia de controles, plan, aprobación y apply. Un `apply` exitoso por sí solo no demuestra que la página esté disponible.

La instancia necesita una AMI Linux compatible con `systemd`, `curl` y nginx, una subnet pública con la ruta requerida y un Security Group que permita HTTP TCP/80 según la arquitectura de referencia. La plantilla no necesita SSH.

## 4. Comprueba el resultado

Haz las verificaciones con fuentes independientes:

1. **Terraform:** revisa outputs como Instance ID e IP pública.
2. **AWS:** confirma por AWS CLI o el mecanismo autorizado que la instancia existe y corresponde a tu despliegue.
3. **HTTP:** abre `http://<ip-publica>/` en el navegador o ejecuta:

```bash
curl -I http://<ip-publica>/
curl http://<ip-publica>/
curl http://<ip-publica>/health.txt
```

La página debe mostrar el estado **operativo**, la versión **v1**, tus datos y los datos de la instancia. `health.txt` devuelve `ok`. La IP pública de la vista previa (`203.0.113.42`) es ficticia: usa la IP real que recibiste en AWS.

Después, revisa el plan posterior, ejecuta la limpieza autorizada y verifica que los recursos evaluados fueron retirados, tal como indique la evaluación.

## Si la página no aparece

- Comprueba que la instancia esté en estado `running` y tenga IP pública.
- Revisa la ruta hacia Internet Gateway y el ingreso HTTP TCP/80 del Security Group.
- Comprueba los registros de arranque mediante los mecanismos permitidos por el entorno.
- Confirma que la AMI elegida sirva el directorio `/usr/share/nginx/html/`, donde la plantilla escribe el portal. Algunas distribuciones usan otro directorio por defecto; utiliza la AMI indicada por el docente y comunica esa incompatibilidad si aparece.
- Si los datos de instancia dicen `No disponible`, revisa que IMDS esté habilitado y que la configuración exija IMDSv2.

El diseño de la página es parte del artefacto entregado. La evidencia evaluable proviene de su integración con Terraform, el despliegue automatizado y las verificaciones solicitadas.
