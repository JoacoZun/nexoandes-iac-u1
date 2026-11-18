resource "aws_lb" "portal" {
  name               = "${var.contract.name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = [for subnet in aws_subnet.public : subnet.id]
  tags               = var.contract.tags
}
resource "aws_lb_target_group" "portal" {
  name                 = "${var.contract.name}-tg"
  port                 = 80
  protocol             = "HTTP"
  target_type          = "instance"
  vpc_id               = aws_vpc.portal.id
  deregistration_delay = var.deployment.deregistration_seconds
  health_check {
    enabled             = true
    path                = var.contract.health_path
    matcher             = "200"
    interval            = 15
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
  tags = var.contract.tags
}
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.portal.arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.portal.arn
  }
  tags = var.contract.tags
}
