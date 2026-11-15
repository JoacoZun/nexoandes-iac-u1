provider "aws" {
  region              = var.deployment.region
  allowed_account_ids = [var.deployment.account_id]
}

# Solo expresiones/contratos, también mantiene la convención Azure sin desplegarla.
module "composition" {
  source      = "../"
  x           = var.x
  x_ratified  = var.x_ratified
  course      = var.course
  build_ref   = var.build_ref
  app_version = var.app_version
}

module "infrastructure" {
  source                  = "./modules/infrastructure"
  contract                = module.composition.contracts.aws
  deployment              = var.deployment
  x_ratified              = var.x_ratified
  enable_instance_refresh = var.enable_instance_refresh
}
