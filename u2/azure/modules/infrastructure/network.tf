resource "azurerm_resource_group" "portal" {
  name     = "${var.contract.name}-rg"
  location = var.deployment.location
  tags     = var.contract.tags
  lifecycle {
    precondition {
      condition     = var.x_ratified
      error_message = "X provisional: ratificar la asignación docente U2 antes de operar Azure."
    }
  }
}
resource "azurerm_virtual_network" "portal" {
  name                = "${var.contract.name}-vnet"
  location            = azurerm_resource_group.portal.location
  resource_group_name = azurerm_resource_group.portal.name
  address_space       = [var.contract.vnet_cidr]
  tags                = var.contract.tags
}
resource "azurerm_subnet" "portal" {
  name                            = "${var.contract.name}-subnet"
  resource_group_name             = azurerm_resource_group.portal.name
  virtual_network_name            = azurerm_virtual_network.portal.name
  address_prefixes                = [var.contract.subnet_cidr]
  default_outbound_access_enabled = false
}
resource "azurerm_network_security_group" "portal" {
  name                = "${var.contract.name}-nsg"
  location            = azurerm_resource_group.portal.location
  resource_group_name = azurerm_resource_group.portal.name
  tags                = var.contract.tags
}
resource "azurerm_network_security_rule" "http" {
  name                        = "HTTP-authorized"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "80"
  source_address_prefixes     = var.deployment.allowed_http_cidrs
  destination_address_prefix  = "*"
  resource_group_name         = azurerm_resource_group.portal.name
  network_security_group_name = azurerm_network_security_group.portal.name
}
resource "azurerm_network_security_rule" "deny_other_inbound" {
  name                        = "Deny-other-inbound"
  priority                    = 4096
  direction                   = "Inbound"
  access                      = "Deny"
  protocol                    = "*"
  source_port_range           = "*"
  destination_port_range      = "*"
  source_address_prefix       = "*"
  destination_address_prefix  = "*"
  resource_group_name         = azurerm_resource_group.portal.name
  network_security_group_name = azurerm_network_security_group.portal.name
}
resource "azurerm_public_ip" "portal" {
  name                = "${var.contract.name}-pip"
  location            = azurerm_resource_group.portal.location
  resource_group_name = azurerm_resource_group.portal.name
  allocation_method   = "Static"
  sku                 = "Standard"
  ip_version          = "IPv4"
  tags                = var.contract.tags
}
resource "azurerm_network_interface" "portal" {
  name                = "${var.contract.name}-nic"
  location            = azurerm_resource_group.portal.location
  resource_group_name = azurerm_resource_group.portal.name
  ip_configuration {
    name                          = "portal"
    subnet_id                     = azurerm_subnet.portal.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.portal.id
  }
  tags = var.contract.tags
}
resource "azurerm_network_interface_security_group_association" "portal" {
  network_interface_id      = azurerm_network_interface.portal.id
  network_security_group_id = azurerm_network_security_group.portal.id
}
