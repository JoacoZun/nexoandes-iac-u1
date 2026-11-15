variable "x" {
  description = "Asignación provisional heredada de U1; requiere ratificación docente U2."
  type        = number
  default     = 8
  nullable    = false
  validation {
    condition     = var.x >= 1 && var.x <= 254 && floor(var.x) == var.x
    error_message = "X debe ser un entero de 1 a 254."
  }
}

variable "x_ratified" {
  description = "Confirmación explícita de la asignación U2; false permite diseñar localmente, nunca autoriza cloud."
  type        = bool
  default     = false
  nullable    = false
}

variable "course" {
  description = "Curso real cNN, obligatorio; no se asume c01."
  type        = string
  nullable    = false
  validation {
    condition     = can(regex("^c[0-9]{2}$", var.course))
    error_message = "Indique el curso real con formato cNN."
  }
}

variable "build_ref" {
  description = "Referencia real de código/artefacto, sin secretos; no acredita un despliegue."
  type        = string
  nullable    = false
  validation {
    condition     = can(regex("^[A-Za-z0-9._-]{4,80}$", var.build_ref))
    error_message = "build_ref requiere 4–80 letras, números, punto, guion o guion bajo."
  }
}

variable "app_version" {
  description = "Versión deseada en AWS; Azure permanece en v1."
  type        = string
  default     = "v1"
  nullable    = false
  validation {
    condition     = contains(["v1", "v2"], var.app_version)
    error_message = "La versión AWS debe ser v1 o v2."
  }
}
