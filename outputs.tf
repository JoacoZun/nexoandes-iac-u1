output "instance_id" {
  description = "Instancia a correlacionar con AWS CLI y limpieza."
  value       = module.compute.instance_id
}

output "public_ip" {
  description = "IPv4 pública para verificación independiente."
  value       = module.compute.public_ip
}

output "portal_url" {
  description = "URL HTTP; su existencia no demuestra disponibilidad del portal."
  value       = "http://${module.compute.public_ip}"
}

output "vpc_id" {
  description = "VPC creada para verificar y limpiar."
  value       = module.network.vpc_id
}

output "subnet_cidr" {
  description = "CIDR derivado del número de lista."
  value       = module.network.subnet_cidr
}

output "security_group_id" {
  description = "Security Group efectivo de la instancia."
  value       = module.security.security_group_id
}
output "subnet_id" {
  description = "Subnet para correlación independiente con AWS."
  value       = module.network.subnet_id
}

output "root_volume_id" {
  description = "EBS raíz para verificar limpieza."
  value       = module.compute.root_volume_id
}
