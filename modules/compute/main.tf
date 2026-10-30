data "aws_ami" "al2023" {
  count       = var.ami_id == null ? 1 : 0
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }
}

resource "aws_instance" "portal" {
  ami                         = var.ami_id != null ? var.ami_id : data.aws_ami.al2023[0].id
  instance_type               = var.instance_type
  subnet_id                   = var.subnet_id
  vpc_security_group_ids      = [var.security_group_id]
  associate_public_ip_address = true
  user_data                   = var.user_data
  user_data_replace_on_change = true

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
    instance_metadata_tags      = "disabled"
  }
  root_block_device {
    encrypted             = true
    volume_type           = "gp3"
    delete_on_termination = true
  }
  tags        = merge(var.tags, { Name = "${var.name}-portal" })
  volume_tags = var.tags

  lifecycle {
    precondition {
      condition     = length(trimspace(var.user_data)) > 0
      error_message = "Falta la plantilla docente o su renderizado falló. No se permite EC2 sin bootstrap oficial."
    }
  }
}
