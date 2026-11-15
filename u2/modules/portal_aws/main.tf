locals {
  contract = {
    name               = "${var.name}-aws"
    tags               = var.tags
    vpc_cidr           = "10.${var.x}.0.0/16"
    subnet_cidrs       = ["10.${var.x}.10.0/24", "10.${var.x}.20.0/24"]
    availability_zones = "two_distinct_authorized_zones_pending"
    endpoint_type      = "alb_dns"
    ingress_path       = "authorized_origins_to_alb_sg_to_ec2_sg_tcp80"
    health_path        = "/health"
    functional_paths   = ["/api/info", "/api/check"]
    user_data_base64   = base64encode(var.bootstrap)
    bootstrap_sha256   = sha256(var.bootstrap)
    portal_version     = var.portal_version
    base_capacity      = "pending_quota_and_strategy_decision"
    controller         = "pending_single_controller_decision"
    deployed           = false
  }
}
