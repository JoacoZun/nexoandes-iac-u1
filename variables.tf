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
    condition     = var.list_number >= 1 && var.list_number <= 254 && floor(var.list_number) == var.list_number
    error_message = "X debe ser un entero entre 1 y 254, según la guía oficial."
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

variable "student_name" {
  description = "Nombre académico real que muestra el portal; es distinto de student_id."
  type        = string
  validation {
    condition = (
      var.student_name == trimspace(var.student_name) &&
      length(var.student_name) >= 2 && length(var.student_name) <= 100 &&
      alltrue([for forbidden in ["\"", "$", "`", "\\", "\n", "\r"] : !strcontains(var.student_name, forbidden)])
    )
    error_message = "Use el nombre académico real (2–100 caracteres), sin bordes en blanco ni caracteres de expansión de shell."
  }
}

variable "environment" {
  description = "Ambiente visible y tag de la Fase 1."
  type        = string
  default     = "fase1"
  validation {
    condition     = var.environment == "fase1"
    error_message = "La guía oficial de NexoAndes Fase 1 exige environment = fase1."
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
