terraform {
  required_version = ">= 1.16.6, < 2.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 6.42.0"
    }
  }
}
