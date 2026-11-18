provider "azurerm" {
  features {}
  subscription_id                 = var.deployment.subscription_id
  tenant_id                       = var.deployment.tenant_id
  resource_provider_registrations = "none"
}

module "composition" {
  source      = "../"
  x           = var.x
  x_ratified  = var.x_ratified
  course      = var.course
  build_ref   = var.build_ref
  app_version = "v1"
}

module "infrastructure" {
  source     = "./modules/infrastructure"
  contract   = module.composition.contracts.azure
  deployment = var.deployment
  x_ratified = var.x_ratified
}
