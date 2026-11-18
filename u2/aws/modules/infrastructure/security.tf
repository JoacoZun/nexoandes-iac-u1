resource "aws_security_group" "alb" {
  name_prefix = "${var.contract.name}-alb-"
  description = "HTTP desde origenes autorizados hacia ALB"
  vpc_id      = aws_vpc.portal.id
  tags        = merge(var.contract.tags, { Name = "${var.contract.name}-alb" })
}
resource "aws_security_group" "ec2" {
  name_prefix = "${var.contract.name}-ec2-"
  description = "Portal solo desde ALB, sin SSH"
  vpc_id      = aws_vpc.portal.id
  tags        = merge(var.contract.tags, { Name = "${var.contract.name}-ec2" })
}
resource "aws_vpc_security_group_ingress_rule" "alb_http" {
  for_each          = toset(var.deployment.allowed_http_cidrs)
  security_group_id = aws_security_group.alb.id
  cidr_ipv4         = each.value
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80
  description       = "HTTP autorizado"
}
resource "aws_vpc_security_group_ingress_rule" "portal_http" {
  security_group_id            = aws_security_group.ec2.id
  referenced_security_group_id = aws_security_group.alb.id
  ip_protocol                  = "tcp"
  from_port                    = 80
  to_port                      = 80
  description                  = "Aplicacion y health check solo desde ALB"
}
resource "aws_vpc_security_group_egress_rule" "alb_portal" {
  security_group_id            = aws_security_group.alb.id
  referenced_security_group_id = aws_security_group.ec2.id
  ip_protocol                  = "tcp"
  from_port                    = 80
  to_port                      = 80
  description                  = "ALB hacia destinos HTTP"
}
resource "aws_vpc_security_group_egress_rule" "bootstrap" {
  for_each          = toset(["80", "443"])
  security_group_id = aws_security_group.ec2.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = tonumber(each.value)
  to_port           = tonumber(each.value)
  description       = "Repositorios autorizados de la imagen por HTTP/HTTPS"
}
