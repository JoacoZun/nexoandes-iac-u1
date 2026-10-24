output "instance_id" {
  description = "Identificador EC2."
  value       = aws_instance.portal.id
}
output "public_ip" {
  description = "IPv4 pública asignada a EC2."
  value       = aws_instance.portal.public_ip
}
output "root_volume_id" {
  description = "Volumen raíz para verificar eliminación independiente."
  value       = aws_instance.portal.root_block_device[0].volume_id
}
