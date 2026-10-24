mock_provider "aws" {}

run "empty_bootstrap_blocks_compute" {
  command = plan
  module { source = "./modules/compute" }
  variables {
    name              = "mock-empty"
    subnet_id         = "subnet-mock"
    security_group_id = "sg-mock"
    instance_type     = "t3.micro"
    user_data         = ""
    tags              = { Project = "Mock" }
  }
  expect_failures = [aws_instance.portal]
}

run "network_contract" {
  command = apply
  module { source = "./modules/network" }
  variables {
    name        = "mock-network"
    list_number = 255
    tags        = { Project = "Mock" }
  }
  assert {
    condition     = aws_vpc.this.cidr_block == "172.16.0.0/16" && aws_subnet.public.cidr_block == "172.16.255.0/24"
    error_message = "VPC y subnet deben conservar los rangos exigidos, incluido el límite X=255."
  }
  assert {
    condition     = aws_subnet.public.vpc_id == aws_vpc.this.id && aws_internet_gateway.this.vpc_id == aws_vpc.this.id
    error_message = "Subnet e IGW deben pertenecer a la misma VPC."
  }
  assert {
    condition     = aws_route.internet.destination_cidr_block == "0.0.0.0/0" && aws_route.internet.gateway_id == aws_internet_gateway.this.id && aws_route.internet.route_table_id == aws_route_table.public.id
    error_message = "Ruta por defecto debe enlazar la tabla pública y el IGW."
  }
  assert {
    condition     = aws_route_table_association.public.subnet_id == aws_subnet.public.id && aws_route_table_association.public.route_table_id == aws_route_table.public.id
    error_message = "La tabla debe estar asociada a la subnet pública."
  }
}

run "security_contract" {
  command = apply
  module { source = "./modules/security" }
  variables {
    name   = "mock-security"
    vpc_id = "vpc-mock"
    tags   = { Project = "Mock" }
  }
  assert {
    condition     = aws_security_group.web.vpc_id == "vpc-mock" && aws_vpc_security_group_ingress_rule.http.security_group_id == aws_security_group.web.id
    error_message = "SG debe pertenecer a network y recibir su regla HTTP."
  }
  assert {
    condition     = aws_vpc_security_group_ingress_rule.http.from_port == 80 && aws_vpc_security_group_ingress_rule.http.to_port == 80 && aws_vpc_security_group_ingress_rule.http.ip_protocol == "tcp" && aws_vpc_security_group_ingress_rule.http.cidr_ipv4 == "0.0.0.0/0"
    error_message = "Única entrada exigida: TCP/80 público."
  }
  assert {
    condition     = length(aws_vpc_security_group_egress_rule.bootstrap) == 2 && alltrue([for r in aws_vpc_security_group_egress_rule.bootstrap : r.ip_protocol == "tcp" && contains([80, 443], r.from_port) && r.to_port == r.from_port])
    error_message = "Salida limitada a HTTP/HTTPS para bootstrap."
  }
}

run "compute_contract" {
  command = apply
  module { source = "./modules/compute" }
  variables {
    name              = "mock-compute"
    subnet_id         = "subnet-mock"
    security_group_id = "sg-mock"
    instance_type     = "t3.micro"
    user_data         = "# Fixture no funcional: solo prueba mock"
    tags              = { Project = "Mock" }
  }
  assert {
    condition     = aws_instance.portal.metadata_options[0].http_tokens == "required" && aws_instance.portal.metadata_options[0].http_put_response_hop_limit == 1
    error_message = "EC2 debe exigir IMDSv2 con hop limit 1."
  }
  assert {
    condition     = aws_instance.portal.subnet_id == "subnet-mock" && aws_instance.portal.vpc_security_group_ids == toset(["sg-mock"]) && aws_instance.portal.associate_public_ip_address
    error_message = "EC2 debe enlazar subnet y SG recibidos y solicitar IP pública."
  }
  assert {
    condition     = aws_instance.portal.root_block_device[0].encrypted && aws_instance.portal.root_block_device[0].delete_on_termination
    error_message = "Volumen raíz cifrado y eliminado con EC2."
  }
  assert {
    condition     = aws_instance.portal.ami == data.aws_ami.al2023[0].id && aws_instance.portal.user_data_replace_on_change
    error_message = "AMI proviene del data source y un cambio de bootstrap reemplaza EC2."
  }
}
