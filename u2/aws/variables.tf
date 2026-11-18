variable "x" {
  type        = number
  default     = 8
  description = "X provisional heredado de U1. Requiere ratificación U2."
}
variable "x_ratified" {
  type        = bool
  default     = false
  description = "Debe ser true tras ratificación docente antes de operar AWS."
}
variable "course" {
  type        = string
  description = "Curso real cNN; obligatorio, validado por la composición compartida."
}
variable "build_ref" {
  type        = string
  description = "Referencia real del artefacto/código, no evidencia de ejecución."
}
variable "app_version" {
  type        = string
  default     = "v1"
  description = "Versión AWS v1/v2. Cambiarla no inicia nada sin una operación autorizada."
}
variable "deployment" {
  description = "Parámetros AWS autorizados. Sin defaults para cuenta, región, imagen o capacidad."
  nullable    = false
  type = object({
    region                 = string
    account_id             = string
    availability_zones     = list(string)
    ami_id                 = string
    instance_type          = string
    root_device_name       = string
    root_volume_gib        = number
    base_capacity          = number
    temporary_capacity     = number
    allowed_http_cidrs     = list(string)
    warmup_seconds         = number
    health_grace_seconds   = number
    deregistration_seconds = number
  })
  validation {
    condition     = can(regex("^[0-9]{12}$", var.deployment.account_id)) && can(regex("^[a-z]{2}(-[a-z]+)+-[0-9]+$", var.deployment.region))
    error_message = "Indique cuenta de 12 dígitos y región AWS autorizadas."
  }
  validation {
    condition     = length(var.deployment.availability_zones) == 2 && length(toset(var.deployment.availability_zones)) == 2 && alltrue([for az in var.deployment.availability_zones : startswith(az, var.deployment.region) && can(regex("[a-z]$", az))])
    error_message = "Se requieren dos AZ distintas de la región autorizada."
  }
  validation {
    condition     = can(regex("^ami-([0-9a-f]{8}|[0-9a-f]{17})$", var.deployment.ami_id)) && can(regex("^[a-z][a-z0-9]*\\.[a-z0-9]+$", var.deployment.instance_type)) && startswith(var.deployment.root_device_name, "/dev/")
    error_message = "Indique AMI, tipo y dispositivo raíz compatibles y autorizados."
  }
  validation {
    condition     = var.deployment.base_capacity >= 1 && floor(var.deployment.base_capacity) == var.deployment.base_capacity && var.deployment.temporary_capacity >= 1 && var.deployment.temporary_capacity <= var.deployment.base_capacity && floor(var.deployment.temporary_capacity) == var.deployment.temporary_capacity && floor(100 * (var.deployment.base_capacity + var.deployment.temporary_capacity) / max(1, var.deployment.base_capacity)) > 100
    error_message = "Capacidad base entera >=1; margen entero entre 1 y base (rolling 100–200%)."
  }
  validation {
    condition     = length(var.deployment.allowed_http_cidrs) > 0 && alltrue([for cidr in var.deployment.allowed_http_cidrs : can(cidrnetmask(cidr))])
    error_message = "Defina al menos un CIDR IPv4 autorizado para HTTP del ALB."
  }
  validation {
    condition     = var.deployment.root_volume_gib >= 8 && floor(var.deployment.root_volume_gib) == var.deployment.root_volume_gib && var.deployment.warmup_seconds >= 0 && var.deployment.warmup_seconds <= 3600 && floor(var.deployment.warmup_seconds) == var.deployment.warmup_seconds && var.deployment.health_grace_seconds >= 0 && floor(var.deployment.health_grace_seconds) == var.deployment.health_grace_seconds && var.deployment.deregistration_seconds >= 0 && var.deployment.deregistration_seconds <= 3600 && floor(var.deployment.deregistration_seconds) == var.deployment.deregistration_seconds
    error_message = "Disco entero >=8 GiB y tiempos enteros válidos; warmup/drenaje 0–3600 s."
  }
}
variable "enable_instance_refresh" {
  type        = bool
  default     = false
  description = "Opt-in futuro: un apply autorizado puede iniciar rolling al cambiar Launch Template. No habilitado en esta preparación."
}
