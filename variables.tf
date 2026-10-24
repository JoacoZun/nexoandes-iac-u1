variable "aws_region" {
  description = "Región explícitamente autorizada por el laboratorio."
  type        = string
  validation {
    condition     = can(regex("^[a-z]{2}(-[a-z]+)+-[0-9]+$", var.aws_region))
    error_message = "Indique una región AWS válida y autorizada."
  }
}

variable "list_number" {
  description = "Número de lista X; determina 172.16.X.0/24. Estudiante actual: 8; se puede sobrescribir."
  type        = number
  default     = 8
  validation {
    condition     = var.list_number >= 0 && var.list_number <= 255 && floor(var.list_number) == var.list_number
    error_message = "X debe ser un entero entre 0 y 255; confirmar el número con el docente."
  }
}

variable "student_id" {
  description = "Identificador académico sin datos sensibles, para nombres y tags."
  type        = string
  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]{1,31}$", var.student_id))
    error_message = "Use entre 2 y 32 caracteres: minúsculas, números y guiones."
  }
}

variable "environment" {
  description = "Ambiente del laboratorio."
  type        = string
  default     = "lab"
  validation {
    condition     = contains(["lab", "dev", "test"], var.environment)
    error_message = "Ambiente permitido: lab, dev o test."
  }
}

variable "instance_type" {
  description = "Tipo x86_64 permitido por el laboratorio; sin asumir elegibilidad gratuita."
  type        = string
  validation {
    condition     = can(regex("^[a-z][a-z0-9]*\\.[a-z0-9]+$", var.instance_type))
    error_message = "Indique un tipo EC2 válido y confirme autorización y arquitectura x86_64."
  }
}

variable "ami_id" {
  description = "AMI x86_64 autorizada; null selecciona Amazon Linux 2023 mediante data source."
  type        = string
  default     = null
  nullable    = true
  validation {
    condition     = var.ami_id == null ? true : can(regex("^ami-([0-9a-f]{8}|[0-9a-f]{17})$", var.ami_id))
    error_message = "Indique un ID AMI válido o null."
  }
}

variable "user_data_template_path" {
  description = "Ruta de la plantilla OFICIAL, relativa al root o absoluta. Obligatoria; no hay reemplazo."
  type        = string
  validation {
    condition     = endswith(var.user_data_template_path, ".tpl")
    error_message = "La ruta debe apuntar a la plantilla oficial .tpl."
  }
}

variable "portal_parameters" {
  description = "Mapa de parámetros según contrato de la plantilla docente; sin secretos."
  type        = map(string)
  default     = {}
}
