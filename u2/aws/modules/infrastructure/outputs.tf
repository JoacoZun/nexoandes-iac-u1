output "endpoint" {
  value = {
    dns_name = aws_lb.portal.dns_name
    url      = "http://${aws_lb.portal.dns_name}"
  }
}
output "ids" {
  value = {
    vpc_id                = aws_vpc.portal.id
    internet_gateway_id   = aws_internet_gateway.portal.id
    route_table_id        = aws_route_table.public.id
    internet_route_id     = aws_route.internet.id
    route_association_ids = [for association in aws_route_table_association.public : association.id]
    subnet_ids            = [for subnet in aws_subnet.public : subnet.id]
    alb_arn               = aws_lb.portal.arn
    target_group_arn      = aws_lb_target_group.portal.arn
    listener_arn          = aws_lb_listener.http.arn
    alb_sg_id             = aws_security_group.alb.id
    ec2_sg_id             = aws_security_group.ec2.id
    launch_template_id    = aws_launch_template.portal.id
    asg_name              = aws_autoscaling_group.portal.name
  }
}
output "controller" {
  value = {
    kind                    = "ASG_Instance_Refresh_Rolling"
    enabled                 = var.enable_instance_refresh
    owner                   = "terraform_aws_provider_only_when_enabled"
    asg_name                = aws_autoscaling_group.portal.name
    launch_template_id      = aws_launch_template.portal.id
    launch_template_version = aws_launch_template.portal.latest_version
    min_healthy_percentage  = 100
    max_healthy_percentage  = local.max_healthy_percentage
    base_capacity           = var.deployment.base_capacity
    temporary_capacity      = var.deployment.temporary_capacity
    warmup_seconds          = var.deployment.warmup_seconds
    portal_version          = var.contract.portal_version
    execution_id            = null
    completion_observed     = false
    requires_external_wait  = true
  }
}
