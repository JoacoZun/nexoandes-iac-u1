output "endpoint" {
  description = "IPv4 pública/URL asignada por Azure; no acredita función del Portal."
  value       = module.infrastructure.endpoint
}
output "ids" {
  description = "IDs reales de recursos tras despliegue, no valores inventados."
  value       = module.infrastructure.ids
}
output "portal" {
  description = "Identidad/build y versión deseada; no evidencia de respuesta HTTP."
  value = {
    identity         = module.composition.identity
    provider         = "azure"
    version          = "v1"
    bootstrap_sha256 = module.composition.contracts.azure.bootstrap_sha256
    functional_paths = ["/api/info", "/api/check"]
  }
}
output "context" {
  description = "Contexto y key esperada; configurar el backend real por separado."
  value = {
    subscription_id    = var.deployment.subscription_id
    tenant_id          = var.deployment.tenant_id
    location           = var.deployment.location
    expected_state_key = module.composition.contexts.azure.state_key
  }
}
