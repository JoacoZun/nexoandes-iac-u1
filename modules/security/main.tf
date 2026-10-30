resource "aws_security_group" "web" {
  name_prefix = "${var.name}-web-"
  description = "Portal HTTP publico; sin acceso SSH; salida solo HTTP y HTTPS"
  vpc_id      = var.vpc_id
  tags        = merge(var.tags, { Name = "${var.name}-web" })
}

resource "aws_vpc_security_group_ingress_rule" "http" {
  security_group_id = aws_security_group.web.id
  description       = "HTTP publico obligatorio en Fase 1"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80
}

resource "aws_vpc_security_group_egress_rule" "bootstrap" {
  for_each          = toset(["80", "443"])
  security_group_id = aws_security_group.web.id
  description       = "Repositorios y dependencias del bootstrap por HTTP o HTTPS"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = tonumber(each.value)
  to_port           = tonumber(each.value)
}
