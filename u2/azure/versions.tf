terraform {
  required_version = ">= 1.16.6, < 2.0.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "= 4.65.0"
    }
  }
  # Backend independiente, pendiente de storage account/container/key U2 autorizados.
  backend "azurerm" {
    use_azuread_auth = true
  }
}
