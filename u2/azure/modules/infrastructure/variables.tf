variable "contract" {
  type = object({
    name           = string
    tags           = map(string)
    vnet_cidr      = string
    subnet_cidr    = string
    custom_data    = string
    portal_version = string
  })
}
variable "deployment" {
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
}
variable "x_ratified" { type = bool }
