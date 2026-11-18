terraform {
  required_version = ">= 1.16.6, < 2.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 6.42.0"
    }
  }
  # Backend parcial: key omitida hasta ratificar curso y X (ver BACKEND.md).
  # Nunca inicializar contra el backend o key de U1.
  backend "s3" {
    bucket       = "nexoandes-tfstate-est8-1793333880"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }
}
