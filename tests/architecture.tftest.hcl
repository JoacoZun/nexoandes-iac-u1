mock_provider "aws" {}

variables {
  aws_region              = "us-east-1" # Dato sintético; no selecciona región de despliegue.
  list_number             = 8
  student_id              = "test-student"
  instance_type           = "t3.micro"
  user_data_template_path = "tests/fixtures/bootstrap.sh.tpl"
  portal_parameters       = { project = "mock-only" }
}

run "root_wiring" {
  command = apply # Solo provider mock; no llamadas AWS.
  assert {
    condition     = output.subnet_cidr == "172.16.8.0/24"
    error_message = "El número de lista 8 debe producir exactamente 172.16.8.0/24."
  }
  assert {
    condition     = output.instance_id != "" && output.security_group_id != "" && output.vpc_id != ""
    error_message = "Los outputs de módulos deben conectarse al root."
  }
  assert {
    condition     = local.tags.ListNumber == "8" && local.tags.Student == var.student_id && endswith(local.name, var.student_id)
    error_message = "Nombres y tags deben usar la misma identidad y el número de lista configurado."
  }
}

run "invalid_list_high" {
  command = plan
  variables { list_number = 256 }
  expect_failures = [var.list_number]
}

run "invalid_list_fraction" {
  command = plan
  variables { list_number = 1.5 }
  expect_failures = [var.list_number]
}

run "invalid_list_negative" {
  command = plan
  variables { list_number = -1 }
  expect_failures = [var.list_number]
}
