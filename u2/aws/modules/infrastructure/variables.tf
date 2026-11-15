variable "contract" {
  description = "Contrato AWS compartido de U2; bootstrap ya codificado exactamente una vez."
  type = object({
    name             = string
    tags             = map(string)
    vpc_cidr         = string
    subnet_cidrs     = list(string)
    user_data_base64 = string
    health_path      = string
    portal_version   = string
  })
}
variable "deployment" {
  description = "Configuración validada por el root AWS, sin consultas data source."
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
}
variable "x_ratified" { type = bool }
variable "enable_instance_refresh" { type = bool }
