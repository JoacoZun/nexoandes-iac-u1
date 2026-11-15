locals {
  identity = {
    x         = var.x
    student   = format("a%03d", var.x)
    course    = var.course
    build_ref = var.build_ref
  }
  name = "na-u2-${var.course}-${local.identity.student}"
  tags = {
    proyecto = "NexoAndes"
    fase     = "U2"
    alumno   = local.identity.student
    curso    = var.course
  }
  template_path = "${path.module}/templates/user_data_u2.sh.tpl"
  bootstraps = {
    aws = templatefile(local.template_path, merge(local.identity, {
      provider       = "aws"
      portal_version = var.app_version
    }))
    azure = templatefile(local.template_path, merge(local.identity, {
      provider       = "azure"
      portal_version = "v1"
    }))
  }
}

# Contratos locales puros: no declaran providers ni recursos cloud.
module "aws" {
  source         = "./modules/portal_aws"
  name           = local.name
  x              = var.x
  tags           = merge(local.tags, { proveedor = "aws" })
  bootstrap      = local.bootstraps.aws
  portal_version = var.app_version
}

module "azure" {
  source    = "./modules/portal_azure"
  name      = local.name
  x         = var.x
  tags      = merge(local.tags, { proveedor = "azure" })
  bootstrap = local.bootstraps.azure
}
