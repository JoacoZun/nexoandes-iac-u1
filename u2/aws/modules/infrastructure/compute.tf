locals {
  bootstrap_bytes = length(var.contract.user_data_base64) * 3 / 4 - (endswith(var.contract.user_data_base64, "==") ? 2 : endswith(var.contract.user_data_base64, "=") ? 1 : 0)
  # floor limita el máximo porcentual al margen entero disponible; >=1 reemplazo.
  max_healthy_percentage = min(200, floor(100 * (var.deployment.base_capacity + var.deployment.temporary_capacity) / max(1, var.deployment.base_capacity)))
}
resource "aws_launch_template" "portal" {
  name_prefix            = "${var.contract.name}-"
  image_id               = var.deployment.ami_id
  instance_type          = var.deployment.instance_type
  user_data              = var.contract.user_data_base64
  update_default_version = false
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
    instance_metadata_tags      = "disabled"
  }
  network_interfaces {
    device_index                = 0
    associate_public_ip_address = true # Salida de bootstrap por IGW; SG bloquea HTTP directo.
    delete_on_termination       = true
    security_groups             = [aws_security_group.ec2.id]
  }
  block_device_mappings {
    device_name = var.deployment.root_device_name
    ebs {
      encrypted             = true
      delete_on_termination = true
      volume_type           = "gp3"
      volume_size           = var.deployment.root_volume_gib
    }
  }
  dynamic "tag_specifications" {
    for_each = toset(["instance", "volume", "network-interface"])
    content {
      resource_type = tag_specifications.value
      tags          = merge(var.contract.tags, { Name = "${var.contract.name}-portal" })
    }
  }
  tags = var.contract.tags
  lifecycle {
    precondition {
      condition     = local.bootstrap_bytes > 0 && local.bootstrap_bytes <= 16384
      error_message = "Bootstrap vacío o potencialmente superior a 16 KiB antes de base64."
    }
  }
}
resource "aws_autoscaling_group" "portal" {
  name                      = "${var.contract.name}-asg"
  min_size                  = var.deployment.base_capacity
  desired_capacity          = var.deployment.base_capacity
  max_size                  = var.deployment.base_capacity + var.deployment.temporary_capacity
  vpc_zone_identifier       = [for subnet in aws_subnet.public : subnet.id]
  target_group_arns         = [aws_lb_target_group.portal.arn]
  health_check_type         = "ELB"
  health_check_grace_period = var.deployment.health_grace_seconds
  default_instance_warmup   = var.deployment.warmup_seconds
  min_elb_capacity          = var.deployment.base_capacity
  wait_for_capacity_timeout = "20m"
  force_delete              = false
  launch_template {
    id      = aws_launch_template.portal.id
    version = tostring(aws_launch_template.portal.latest_version) # Número concreto, nunca $Latest.
  }
  instance_maintenance_policy {
    min_healthy_percentage = 100
    max_healthy_percentage = local.max_healthy_percentage
  }
  dynamic "instance_refresh" {
    for_each = var.enable_instance_refresh ? [true] : []
    content {
      strategy = "Rolling"
      preferences {
        min_healthy_percentage       = 100
        max_healthy_percentage       = local.max_healthy_percentage
        instance_warmup              = var.deployment.warmup_seconds
        skip_matching                = true
        auto_rollback                = false # Recuperación requiere versión conservada y operación controlada.
        scale_in_protected_instances = "Wait"
        standby_instances            = "Wait"
      }
    }
  }
  dynamic "tag" {
    for_each = var.contract.tags
    content {
      key                 = tag.key
      value               = tag.value
      propagate_at_launch = true
    }
  }
  depends_on = [aws_route.internet, aws_route_table_association.public, aws_vpc_security_group_egress_rule.bootstrap, aws_lb_listener.http]
}
