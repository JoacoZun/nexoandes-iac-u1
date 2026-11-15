terraform {
  required_version = ">= 1.16.6, < 2.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 6.42.0"
    }
  }
  # Backend parcial: completar SOLO con almacenamiento U2 autorizado.
  # Nunca inicializar contra el backend o key de U1.
  backend "s3" {
    encrypt      = true
    use_lockfile = true
  }
}
