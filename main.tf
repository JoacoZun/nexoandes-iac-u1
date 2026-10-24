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
  # try permite validate sin plantilla; la precondición EC2 bloquea cualquier plan real.
  user_data = try(templatefile(var.user_data_template_path, var.portal_parameters), "")
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
  user_data         = local.user_data
  tags              = local.tags

  # La subnet existe antes que su ruta; el bootstrap necesita conectividad al arrancar.
  depends_on = [module.network, module.security]
}
