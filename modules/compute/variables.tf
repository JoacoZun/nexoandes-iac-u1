variable "name" {
  description = "Prefijo de nombres."
  type        = string
}
variable "subnet_id" {
  description = "Subnet pública creada por network."
  type        = string
}
variable "security_group_id" {
  description = "Security Group HTTP creado por security."
  type        = string
}
variable "instance_type" {
  description = "Tipo EC2 x86_64 autorizado."
  type        = string
}
variable "ami_id" {
  description = "AMI autorizada o null para Amazon Linux 2023 x86_64."
  type        = string
  default     = null
}
variable "user_data" {
  description = "Plantilla oficial renderizada por root; nunca contiene secretos."
  type        = string
}
variable "tags" {
  description = "Tags comunes de trazabilidad."
  type        = map(string)
}
