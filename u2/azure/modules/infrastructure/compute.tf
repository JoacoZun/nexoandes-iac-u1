locals {
  custom_data_bytes = length(var.contract.custom_data) * 3 / 4 - (endswith(var.contract.custom_data, "==") ? 2 : endswith(var.contract.custom_data, "=") ? 1 : 0)
}
resource "azurerm_linux_virtual_machine" "portal" {
  name                            = "${var.contract.name}-vm"
  location                        = azurerm_resource_group.portal.location
  resource_group_name             = azurerm_resource_group.portal.name
  size                            = var.deployment.vm_size
  admin_username                  = var.deployment.admin_username
  disable_password_authentication = true
  network_interface_ids           = [azurerm_network_interface.portal.id]
  custom_data                     = var.contract.custom_data
  admin_ssh_key {
    username   = var.deployment.admin_username
    public_key = var.deployment.admin_ssh_public_key
  }
  source_image_reference {
    publisher = var.deployment.image.publisher
    offer     = var.deployment.image.offer
    sku       = var.deployment.image.sku
    version   = var.deployment.image.version
  }
  os_disk {
    name                 = "${var.contract.name}-osdisk"
    caching              = "ReadWrite"
    storage_account_type = var.deployment.storage_account_type
    disk_size_gb         = var.deployment.os_disk_size_gib
  }
  tags = var.contract.tags
  depends_on = [
    azurerm_network_interface_security_group_association.portal,
    azurerm_network_security_rule.http,
    azurerm_network_security_rule.deny_other_inbound
  ]
  lifecycle {
    precondition {
      condition     = var.contract.portal_version == "v1"
      error_message = "Azure U2 debe permanecer en Portal v1."
    }
    precondition {
      condition     = local.custom_data_bytes > 0 && local.custom_data_bytes <= 65536
      error_message = "custom_data debe contener el bootstrap base64 dentro del límite Azure de 64 KiB."
    }
  }
}
