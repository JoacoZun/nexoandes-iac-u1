terraform {
  backend "s3" {
    bucket       = "nexoandes-tfstate-est8-1793333880"
    key          = "fase1/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }
}
