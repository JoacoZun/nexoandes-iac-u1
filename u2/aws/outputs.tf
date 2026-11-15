output "endpoint" {
  description = "Endpoint de servicio ALB; no demuestra disponibilidad funcional."
  value       = module.infrastructure.endpoint
}
output "ids" {
  description = "Identificadores de recursos gestionados; EC2 dinámicas se consultarán al ASG."
  value       = module.infrastructure.ids
}
output "controller" {
  description = "Configuración del controlador; no es ID/estado de una ejecución Instance Refresh."
  value       = module.infrastructure.controller
}
output "context" {
  description = "Contexto y key U2 esperada; backend real requiere configuración independiente."
  value = {
    account_id         = var.deployment.account_id
    region             = var.deployment.region
    expected_state_key = module.composition.contexts.aws.state_key
    identity           = module.composition.identity
  }
}
