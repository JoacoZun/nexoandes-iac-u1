variable "name" {
  description = "Prefijo común de nombres."
  type        = string
}
variable "list_number" {
  description = "Octeto X dentro de la VPC fija 172.16.0.0/16."
  type        = number
  validation {
    condition     = var.list_number >= 0 && var.list_number <= 255 && floor(var.list_number) == var.list_number
    error_message = "X debe ser un entero entre 0 y 255."
  }
}
variable "tags" {
  description = "Tags de trazabilidad."
  type        = map(string)
}
