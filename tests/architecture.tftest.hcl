mock_provider "aws" {}

variables {
  aws_region    = "us-east-1" # Dato sintético; no selecciona región de despliegue.
  list_number   = 8
  student_id    = "test-student"
  student_name  = "Test Student"
  instance_type = "t3.micro"
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
  assert {
    condition = alltrue([
      strcontains(local.portal_user_data, "STUDENT_NAME=\"Test Student\""),
      strcontains(local.portal_user_data, "STUDENT_NUMBER=\"8\""),
      strcontains(local.portal_user_data, "ENVIRONMENT=\"fase1\""),
      strcontains(local.portal_user_data, "PORTAL_VERSION=\"v1\""),
      strcontains(local.portal_user_data, "PROJECT_NAME=\"NexoAndes Portal Operacional\"")
    ])
    error_message = "templatefile debe renderizar exactamente los cinco parámetros oficiales."
  }
  assert {
    condition = alltrue([
      strcontains(local.portal_user_data, "dnf install -y nginx"),
      strcontains(local.portal_user_data, "yum install -y nginx"),
      strcontains(local.portal_user_data, "apt-get install -y nginx"),
      strcontains(local.portal_user_data, "http://169.254.169.254/latest/api/token"),
      strcontains(local.portal_user_data, "/usr/share/nginx/html/index.html"),
      strcontains(local.portal_user_data, "/usr/share/nginx/html/health.txt"),
      strcontains(local.portal_user_data, "$${path}"),
      strcontains(local.portal_user_data, "$${E_PORTAL_VERSION}")
    ])
    error_message = "El renderizado debe conservar instrucciones oficiales y expresiones destinadas a Bash."
  }
}

run "invalid_list_high" {
  command = plan
  variables { list_number = 255 }
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
