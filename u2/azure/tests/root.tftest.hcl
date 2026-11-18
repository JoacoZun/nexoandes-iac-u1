# Identidad académica indicada por el usuario: X=8/a008/c50 (sección 50 asumida).
# Suscripción, ubicación, imagen, IP, clave y build son fixtures sintéticas.
# Sin provider real, apply, credenciales ni acceso cloud.
mock_provider "azurerm" {
  override_during = plan
  mock_resource "azurerm_resource_group" { defaults = { id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/na-u2-c50-a008-az-rg" } }
  mock_resource "azurerm_virtual_network" { defaults = { id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/na-u2-c50-a008-az-rg/providers/Microsoft.Network/virtualNetworks/test-vnet" } }
  mock_resource "azurerm_subnet" { defaults = { id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/na-u2-c50-a008-az-rg/providers/Microsoft.Network/virtualNetworks/test-vnet/subnets/test-subnet" } }
  mock_resource "azurerm_public_ip" { defaults = { id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/na-u2-c50-a008-az-rg/providers/Microsoft.Network/publicIPAddresses/test-pip", ip_address = "192.0.2.8" } }
  mock_resource "azurerm_network_interface" { defaults = { id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/na-u2-c50-a008-az-rg/providers/Microsoft.Network/networkInterfaces/test-nic", private_ip_address = "172.20.8.4" } }
  mock_resource "azurerm_network_security_group" { defaults = { id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/na-u2-c50-a008-az-rg/providers/Microsoft.Network/networkSecurityGroups/test-nsg" } }
}
variables {
  x          = 8
  course     = "c50"
  build_ref  = "offline-test"
  x_ratified = true
  deployment = {
    subscription_id      = "00000000-0000-0000-0000-000000000001"
    tenant_id            = "00000000-0000-0000-0000-000000000002"
    location             = "eastus"
    vm_size              = "Standard_B1s"
    admin_username       = "offlineuser"
    admin_ssh_public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADA5 offline-fixture-not-for-access"
    allowed_http_cidrs   = ["192.0.2.0/24"]
    os_disk_size_gib     = 30
    storage_account_type = "Standard_LRS"
    image                = { publisher = "Canonical", offer = "offline-fixture", sku = "offline-fixture", version = "1.0.0" }
  }
}

run "azure_v1_identity_endpoint_and_state" {
  command = plan
  assert {
    condition     = output.portal.version == "v1" && output.portal.provider == "azure" && output.portal.identity.x == 8 && output.portal.identity.x_ratified && output.portal.identity.student == "a008" && output.portal.identity.course == "c50"
    error_message = "Identidad y versión Azure deben conservar el contrato."
  }
  assert {
    condition     = output.context.expected_state_key == "u2/c50/a008/azure/terraform.tfstate" && output.endpoint.url == "http://192.0.2.8"
    error_message = "State Azure independiente y endpoint asignado por provider mock."
  }
  assert {
    condition     = module.composition.contracts.azure.vnet_cidr == "172.20.8.0/24" && module.composition.contracts.azure.subnet_cidr == "172.20.8.0/26" && module.composition.contracts.azure.tags.alumno == "a008" && module.composition.contracts.azure.tags.curso == "c50" && module.composition.contracts.azure.tags.proveedor == "azure"
    error_message = "Red e identidad del contrato Azure deben corresponder a X=8/a008/c50."
  }
}
run "build_changes_bootstrap_not_portal_version" {
  command = plan
  variables { build_ref = "offline-second-build" }
  assert {
    condition     = output.portal.version == "v1" && output.portal.identity.build_ref == "offline-second-build"
    error_message = "Azure conserva v1 al cambiar build."
  }
}
