terraform {
  required_version = ">= 1.16.6, < 2.0.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "= 4.65.0"
    }
  }
}
