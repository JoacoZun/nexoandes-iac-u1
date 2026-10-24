variable "name" {
  description = "Prefijo de nombres."
  type        = string
}
variable "vpc_id" {
  description = "VPC del módulo network."
  type        = string
}
variable "tags" {
  description = "Tags de trazabilidad."
  type        = map(string)
}
