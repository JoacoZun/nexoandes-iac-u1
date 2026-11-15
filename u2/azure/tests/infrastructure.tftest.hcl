# Todas las identidades/ubicaciones/imágenes/clave pública son fixtures sintéticas.
# Sin provider real, apply, credenciales ni acceso cloud.
mock_provider "azurerm" {
  override_during = plan
  mock_resource "azurerm_resource_group" { defaults = { id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/na-u2-c99-a008-az-rg" } }
  mock_resource "azurerm_virtual_network" { defaults = { id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/na-u2-c99-a008-az-rg/providers/Microsoft.Network/virtualNetworks/test-vnet" } }
  mock_resource "azurerm_subnet" { defaults = { id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/na-u2-c99-a008-az-rg/providers/Microsoft.Network/virtualNetworks/test-vnet/subnets/test-subnet" } }
  mock_resource "azurerm_public_ip" { defaults = { id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/na-u2-c99-a008-az-rg/providers/Microsoft.Network/publicIPAddresses/test-pip", ip_address = "192.0.2.8" } }
  mock_resource "azurerm_network_interface" { defaults = { id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/na-u2-c99-a008-az-rg/providers/Microsoft.Network/networkInterfaces/test-nic", private_ip_address = "172.20.8.4" } }
  mock_resource "azurerm_network_security_group" { defaults = { id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/na-u2-c99-a008-az-rg/providers/Microsoft.Network/networkSecurityGroups/test-nsg" } }
}
variables {
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
  contract = {
    name           = "na-u2-c99-a008-az"
    tags           = { proyecto = "NexoAndes", fase = "U2", alumno = "a008", curso = "c99", proveedor = "azure" }
    vnet_cidr      = "172.20.8.0/24", subnet_cidr = "172.20.8.0/26"
    custom_data    = "IyEvYmluL2Jhc2gKIyBvZmZsaW5lIGZpeHR1cmUK"
    portal_version = "v1"
  }
}

run "network_http_and_explicit_egress" {
  command = plan
  module { source = "./modules/infrastructure" }
  assert {
    condition     = toset(azurerm_virtual_network.portal.address_space) == toset(["172.20.8.0/24"]) && toset(azurerm_subnet.portal.address_prefixes) == toset(["172.20.8.0/26"]) && !azurerm_subnet.portal.default_outbound_access_enabled
    error_message = "Red Azure U2 y salida predeterminada deshabilitada."
  }
  assert {
    condition     = azurerm_network_security_rule.http.destination_port_range == "80" && azurerm_network_security_rule.http.direction == "Inbound" && azurerm_network_security_rule.deny_other_inbound.access == "Deny" && azurerm_public_ip.portal.sku == "Standard" && azurerm_public_ip.portal.allocation_method == "Static"
    error_message = "HTTP autorizado, deny de resto de entrada e IP Standard estática."
  }
  assert {
    condition     = azurerm_network_interface.portal.ip_configuration[0].private_ip_address_allocation == "Dynamic" && azurerm_network_interface.portal.ip_configuration[0].public_ip_address_id == azurerm_public_ip.portal.id
    error_message = "NIC debe recibir IP privada real y asociar salida explícita por IP pública."
  }
}
run "cloud_init_and_no_password" {
  command = plan
  module { source = "./modules/infrastructure" }
  assert {
    condition     = nonsensitive(azurerm_linux_virtual_machine.portal.custom_data) == var.contract.custom_data && azurerm_linux_virtual_machine.portal.disable_password_authentication && azurerm_linux_virtual_machine.portal.admin_password == null && azurerm_linux_virtual_machine.portal.source_image_reference[0].version == "1.0.0"
    error_message = "VM usa custom_data intacto, imagen fijada y nunca contraseña."
  }
}
run "unratified_x_blocks_resources" {
  command = plan
  module { source = "./modules/infrastructure" }
  variables { x_ratified = false }
  expect_failures = [azurerm_resource_group.portal]
}
run "azure_v2_rejected" {
  command = plan
  module { source = "./modules/infrastructure" }
  variables {
    contract = {
      name           = "na-u2-c99-a008-az"
      tags           = { proyecto = "NexoAndes", fase = "U2", proveedor = "azure" }
      vnet_cidr      = "172.20.8.0/24", subnet_cidr = "172.20.8.0/26"
      custom_data    = "IyEvYmluL2Jhc2gKIyBvZmZsaW5lIGZpeHR1cmUK"
      portal_version = "v2"
    }
  }
  expect_failures = [azurerm_linux_virtual_machine.portal]
}
