locals {
  name = "nexoandes-f1-${var.environment}-${var.student_id}"
  tags = {
    Project     = "NexoAndes"
    Phase       = "fase1"
    Environment = var.environment
    Student     = var.student_id
    ListNumber  = tostring(var.list_number)
    ManagedBy   = "Terraform"
  }
  portal_user_data = templatefile("${path.module}/templates/user_data_v1.sh.tpl", {
    student_name   = var.student_name
    student_number = tostring(var.list_number)
    environment    = var.environment
    portal_version = "v1"
    project_name   = "NexoAndes Portal Operacional"
  })
}

module "network" {
  source      = "./modules/network"
  name        = local.name
  list_number = var.list_number
  tags        = local.tags
}

module "security" {
  source = "./modules/security"
  name   = local.name
  vpc_id = module.network.vpc_id
  tags   = local.tags
}

module "compute" {
  source            = "./modules/compute"
  name              = local.name
  subnet_id         = module.network.subnet_id
  security_group_id = module.security.security_group_id
  instance_type     = var.instance_type
  ami_id            = var.ami_id
  user_data         = local.portal_user_data
  tags              = local.tags

  # La subnet existe antes que su ruta; el bootstrap necesita conectividad al arrancar.
  depends_on = [module.network, module.security]
}
