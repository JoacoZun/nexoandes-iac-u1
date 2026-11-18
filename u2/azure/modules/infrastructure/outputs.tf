output "endpoint" {
  value = {
    public_ip = azurerm_public_ip.portal.ip_address
    url       = "http://${azurerm_public_ip.portal.ip_address}"
  }
}
output "ids" {
  value = {
    resource_group_id = azurerm_resource_group.portal.id
    vnet_id           = azurerm_virtual_network.portal.id
    subnet_id         = azurerm_subnet.portal.id
    nsg_id            = azurerm_network_security_group.portal.id
    nic_id            = azurerm_network_interface.portal.id
    public_ip_id      = azurerm_public_ip.portal.id
    vm_resource_id    = azurerm_linux_virtual_machine.portal.id
    vm_metadata_id    = azurerm_linux_virtual_machine.portal.virtual_machine_id
    private_ip        = azurerm_network_interface.portal.private_ip_address
    os_disk_name      = azurerm_linux_virtual_machine.portal.os_disk[0].name
  }
}
