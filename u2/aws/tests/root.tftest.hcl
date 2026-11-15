# Fixtures synthétiques uniquement. Mock obligatoire, aucun provider réel ni apply.
mock_provider "aws" {
  override_during = plan
  mock_resource "aws_launch_template" { defaults = { id = "lt-00000000000000000", latest_version = 1 } }
}
variables {
  course     = "c99"
  build_ref  = "offline-test"
  x_ratified = true
  deployment = {
    region                 = "us-east-1"
    account_id             = "000000000000"
    availability_zones     = ["us-east-1a", "us-east-1b"]
    ami_id                 = "ami-00000000000000000"
    instance_type          = "t3.micro"
    root_device_name       = "/dev/sda1"
    root_volume_gib        = 8
    base_capacity          = 2
    temporary_capacity     = 1
    allowed_http_cidrs     = ["192.0.2.0/24"]
    warmup_seconds         = 60
    health_grace_seconds   = 120
    deregistration_seconds = 30
  }
}
run "root_contract_and_disabled_controller" {
  command = plan
  assert {
    condition     = !output.controller.enabled && output.controller.execution_id == null && output.controller.requires_external_wait
    error_message = "Refresh debe quedar deshabilitado, sin ejecución inventada y con espera pendiente."
  }
  assert {
    condition     = output.context.expected_state_key == "u2/c99/a008/aws/terraform.tfstate" && output.controller.base_capacity == 2 && output.controller.max_healthy_percentage == 150
    error_message = "Identidad/state y capacidad deben respetar contratos."
  }
  assert {
    condition     = startswith(output.endpoint.url, "http://") && output.ids.asg_name != ""
    error_message = "Distinguir endpoint, IDs y controlador."
  }
}
run "root_v2_is_parameterized_not_started" {
  command = plan
  variables { app_version = "v2" }
  assert {
    condition     = output.controller.portal_version == "v2" && !output.controller.enabled && !output.controller.completion_observed
    error_message = "Seleccionar v2 no acredita ni inicia refresh en estos tests."
  }
}
run "duplicate_az_rejected" {
  command = plan
  variables {
    deployment = {
      region             = "us-east-1", account_id = "000000000000"
      availability_zones = ["us-east-1a", "us-east-1a"]
      ami_id             = "ami-00000000000000000", instance_type = "t3.micro"
      root_device_name   = "/dev/sda1", root_volume_gib = 8
      base_capacity      = 2, temporary_capacity = 1
      allowed_http_cidrs = ["192.0.2.0/24"]
      warmup_seconds     = 60, health_grace_seconds = 120, deregistration_seconds = 30
    }
  }
  expect_failures = [var.deployment]
}
