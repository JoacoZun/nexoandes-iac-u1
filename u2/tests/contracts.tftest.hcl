variables {
  course    = "c99" # Solo fixture; no confirma curso real.
  build_ref = "offline-test"
}

run "provisional_identity_and_networks" {
  command = plan
  assert {
    condition     = output.identity.student == "a008" && !output.identity.x_ratified && !output.readiness.cloud_enabled
    error_message = "La base debe conservar X=8 provisional y cloud deshabilitado."
  }
  assert {
    condition     = output.contracts.aws.vpc_cidr == "10.8.0.0/16" && output.contracts.aws.subnet_cidrs == ["10.8.10.0/24", "10.8.20.0/24"] && output.contracts.azure.subnet_cidr == "172.20.8.0/26"
    error_message = "Redes deben respetar la convención U2."
  }
  assert {
    condition     = output.contexts.aws.state_key != output.contexts.azure.state_key && startswith(output.contexts.aws.state_key, "u2/")
    error_message = "Estados deben distinguir fase y nube."
  }
  assert {
    condition     = length(base64decode(output.contracts.aws.user_data_base64)) > 0 && length(base64decode(output.contracts.azure.custom_data)) > 0
    error_message = "Ambos contratos deben recibir bootstrap renderizado y codificado una vez."
  }
  assert {
    condition = strcontains(base64decode(output.contracts.aws.user_data_base64), base64encode(jsonencode({
      provider = "aws", x = 8, student = "a008", course = "c99", build_ref = "offline-test", portal_version = "v1"
    })))
    error_message = "templatefile debe serializar los seis parámetros AWS dentro del bootstrap."
  }
}

run "aws_v2_azure_stays_v1" {
  command = plan
  variables { app_version = "v2" }
  assert {
    condition     = output.contracts.aws.portal_version == "v2" && output.contracts.azure.portal_version == "v1" && output.contracts.aws.bootstrap_sha256 != output.contracts.azure.bootstrap_sha256
    error_message = "Azure conserva v1 con bootstrap/contexto independiente."
  }
  assert {
    condition     = !output.contracts.aws.deployed && !output.contracts.azure.deployed
    error_message = "Contratos locales no deben fingir recursos desplegados."
  }
}

run "reject_invalid_x" {
  command = plan
  variables { x = 255 }
  expect_failures = [var.x]
}

run "reject_invalid_course" {
  command = plan
  variables { course = "inventado" }
  expect_failures = [var.course]
}

run "reject_shell_build" {
  command = plan
  variables { build_ref = "$(id)" }
  expect_failures = [var.build_ref]
}

run "reject_unknown_release" {
  command = plan
  variables { app_version = "v3" }
  expect_failures = [var.app_version]
}
