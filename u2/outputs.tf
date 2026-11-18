output "identity" {
  description = "Identidad de diseño; X no está ratificado por defecto."
  value       = merge(local.identity, { x_ratified = var.x_ratified })
}

output "contracts" {
  description = "Especificaciones deseadas; no son outputs de infraestructura desplegada."
  value = {
    aws   = module.aws.contract
    azure = module.azure.contract
  }
}

output "contexts" {
  description = "Separación propuesta; no configura ni inicializa backends."
  value = {
    aws = {
      state_key      = "u2/${var.course}/${local.identity.student}/aws/terraform.tfstate"
      provider       = "hashicorp/aws"
      authentication = "pending_authorized_aws_identity"
      destination    = "pending_account_and_region"
    }
    azure = {
      state_key      = "u2/${var.course}/${local.identity.student}/azure/terraform.tfstate"
      provider       = "hashicorp/azurerm"
      authentication = "pending_authorized_azure_identity"
      destination    = "pending_tenant_subscription_and_location"
    }
  }
}

output "readiness" {
  description = "Bloqueos explícitos; esta base nunca autoriza operaciones cloud."
  value = {
    cloud_enabled = false
    x_ratified    = var.x_ratified
    stage         = "local_contracts_only"
    pending       = ["authorized_contexts", "separate_backends", "provider_locks", "cloud_resources", "change_controller", "observation", "approval", "execution_evidence"]
  }
}
