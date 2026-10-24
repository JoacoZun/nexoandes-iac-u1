output "vpc_id" {
  description = "VPC para el módulo security."
  value       = aws_vpc.this.id
}
output "subnet_id" {
  description = "Subnet para el módulo compute."
  value       = aws_subnet.public.id
}
output "subnet_cidr" {
  description = "CIDR efectivo de la subnet."
  value       = aws_subnet.public.cidr_block
}
