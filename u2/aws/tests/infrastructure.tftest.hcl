mock_provider "aws" {
  override_during = plan
  mock_resource "aws_launch_template" { defaults = { id = "lt-00000000000000000", latest_version = 7 } }
}
override_resource {
  target          = aws_security_group.alb
  override_during = plan
  values          = { id = "sg-00000000000000001" }
}
override_resource {
  target          = aws_security_group.ec2
  override_during = plan
  values          = { id = "sg-00000000000000002" }
}
variables {
  x_ratified              = true
  enable_instance_refresh = false
  contract = {
    name             = "na-u2-c99-a008-aws"
    tags             = { proyecto = "NexoAndes", fase = "U2", alumno = "a008", curso = "c99", proveedor = "aws" }
    vpc_cidr         = "10.8.0.0/16", subnet_cidrs = ["10.8.10.0/24", "10.8.20.0/24"]
    user_data_base64 = "IyEvYmluL2Jhc2gKIyBvZmZsaW5lIGZpeHR1cmUK"
    health_path      = "/health", portal_version = "v1"
  }
  deployment = {
    region             = "us-east-1", account_id = "000000000000"
    availability_zones = ["us-east-1a", "us-east-1b"]
    ami_id             = "ami-00000000000000000", instance_type = "t3.micro"
    root_device_name   = "/dev/sda1", root_volume_gib = 8
    base_capacity      = 2, temporary_capacity = 1
    allowed_http_cidrs = ["192.0.2.0/24"]
    warmup_seconds     = 60, health_grace_seconds = 120, deregistration_seconds = 30
  }
}
run "network_security_and_bootstrap" {
  command = plan
  module { source = "./modules/infrastructure" }
  assert {
    condition     = aws_vpc.portal.cidr_block == "10.8.0.0/16" && aws_subnet.public["0"].cidr_block == "10.8.10.0/24" && aws_subnet.public["1"].cidr_block == "10.8.20.0/24" && aws_subnet.public["0"].availability_zone != aws_subnet.public["1"].availability_zone
    error_message = "VPC y dos subredes deben corresponder a X y AZ distintas."
  }
  assert {
    condition     = aws_route.internet.destination_cidr_block == "0.0.0.0/0" && length(aws_route_table_association.public) == 2
    error_message = "Ambas subredes requieren ruta por IGW."
  }
  assert {
    condition     = aws_vpc_security_group_ingress_rule.portal_http.referenced_security_group_id == aws_security_group.alb.id && aws_vpc_security_group_ingress_rule.portal_http.cidr_ipv4 == null && aws_vpc_security_group_ingress_rule.alb_http["192.0.2.0/24"].from_port == 80
    error_message = "EC2 solo acepta HTTP desde SG ALB, nunca desde CIDR público."
  }
  assert {
    condition     = aws_launch_template.portal.user_data == var.contract.user_data_base64 && aws_launch_template.portal.metadata_options[0].http_tokens == "required" && aws_launch_template.portal.block_device_mappings[0].ebs[0].encrypted
    error_message = "Launch Template debe conservar base64, IMDSv2 y EBS cifrado."
  }
  assert {
    condition     = aws_autoscaling_group.portal.desired_capacity == 2 && aws_autoscaling_group.portal.min_size == 2 && aws_autoscaling_group.portal.max_size == 3 && length(aws_autoscaling_group.portal.instance_refresh) == 0 && aws_autoscaling_group.portal.launch_template[0].version == "7"
    error_message = "Base fija, margen temporal, refresh apagado y LT numérica."
  }
}
run "rolling_preferences_without_real_controller" {
  command = plan
  module { source = "./modules/infrastructure" }
  variables { enable_instance_refresh = true }
  assert {
    condition     = aws_autoscaling_group.portal.instance_refresh[0].strategy == "Rolling" && aws_autoscaling_group.portal.instance_refresh[0].preferences[0].min_healthy_percentage == 100 && aws_autoscaling_group.portal.instance_refresh[0].preferences[0].max_healthy_percentage == 150
    error_message = "Rolling debe preservar 100% base y respetar margen temporal."
  }
}
run "unratified_identity_blocks_infrastructure" {
  command = plan
  module { source = "./modules/infrastructure" }
  variables { x_ratified = false }
  expect_failures = [aws_vpc.portal]
}
