variable "x" {
  type        = number
  default     = 8
  description = "X provisional; ratificación docente U2 pendiente."
}
variable "x_ratified" {
  type        = bool
  default     = false
  description = "Confirmación explícita requerida para crear el Resource Group."
}
variable "course" {
  type        = string
  description = "Curso real cNN, validado por la composición compartida."
}
variable "build_ref" {
  type        = string
  description = "Referencia real del código/artefacto, sin secretos."
}
variable "deployment" {
  description = "Contexto, imagen cloud-init y configuración autorizados; sin valores reales predeterminados."
  nullable    = false
  type = object({
    subscription_id      = string
    tenant_id            = string
    location             = string
    vm_size              = string
    admin_username       = string
    admin_ssh_public_key = string
    allowed_http_cidrs   = list(string)
    os_disk_size_gib     = number
    storage_account_type = string
    image = object({
      publisher = string
      offer     = string
      sku       = string
      version   = string
    })
  })
  validation {
    condition     = alltrue([for id in [var.deployment.subscription_id, var.deployment.tenant_id] : can(regex("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$", id))])
    error_message = "Indique UUID de suscripción y tenant autorizados."
  }
  validation {
    condition     = length(trimspace(var.deployment.location)) > 0 && length(trimspace(var.deployment.vm_size)) > 0 && can(regex("^[a-z][a-z0-9_-]{1,30}$", var.deployment.admin_username))
    error_message = "Ubicación y tamaño obligatorios; usuario Linux válido y autorizado."
  }
  validation {
    condition     = can(regex("^ssh-rsa [A-Za-z0-9+/]+={0,2}( .*)?$", trimspace(var.deployment.admin_ssh_public_key))) && !strcontains(var.deployment.admin_ssh_public_key, "PRIVATE KEY")
    error_message = "Proporcione solo clave pública RSA autorizada; nunca una clave privada."
  }
  validation {
    condition     = length(var.deployment.allowed_http_cidrs) > 0 && alltrue([for cidr in var.deployment.allowed_http_cidrs : can(cidrnetmask(cidr))])
    error_message = "Defina al menos un CIDR IPv4 autorizado para HTTP."
  }
  validation {
    condition     = alltrue([for value in [var.deployment.image.publisher, var.deployment.image.offer, var.deployment.image.sku, var.deployment.image.version] : length(trimspace(value)) > 0]) && lower(var.deployment.image.version) != "latest"
    error_message = "Defina publisher/offer/sku y versión exacta de imagen cloud-init; no usar latest."
  }
  validation {
    condition     = var.deployment.os_disk_size_gib >= 1 && floor(var.deployment.os_disk_size_gib) == var.deployment.os_disk_size_gib && contains(["Standard_LRS", "StandardSSD_LRS", "Premium_LRS"], var.deployment.storage_account_type)
    error_message = "Disco entero positivo y tipo de almacenamiento compatible; verificar mínimo de la imagen."
  }
}
