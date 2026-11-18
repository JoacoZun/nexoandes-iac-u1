locals {
  contract = {
    name             = "${var.name}-az"
    tags             = var.tags
    vnet_cidr        = "172.20.${var.x}.0/24"
    subnet_cidr      = "172.20.${var.x}.0/26"
    endpoint_type    = "azure_assigned_public_ip"
    ingress_path     = "authorized_origins_to_nsg_nic_tcp80"
    outbound         = "explicit_authorized_egress_required"
    functional_paths = ["/api/info", "/api/check"]
    custom_data      = base64encode(var.bootstrap)
    bootstrap_sha256 = sha256(var.bootstrap)
    portal_version   = "v1"
    admin_public_key = "pending_authorized_public_key_if_required"
    deployed         = false
  }
}
