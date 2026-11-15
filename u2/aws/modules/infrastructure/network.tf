resource "aws_vpc" "portal" {
  cidr_block           = var.contract.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags                 = merge(var.contract.tags, { Name = "${var.contract.name}-vpc" })
  lifecycle {
    precondition {
      condition     = var.x_ratified
      error_message = "X=8 es provisional. Ratificar la asignación U2 antes de operar AWS."
    }
  }
}
resource "aws_subnet" "public" {
  for_each                = { for i, az in var.deployment.availability_zones : tostring(i) => az }
  vpc_id                  = aws_vpc.portal.id
  cidr_block              = var.contract.subnet_cidrs[tonumber(each.key)]
  availability_zone       = each.value
  map_public_ip_on_launch = false
  tags                    = merge(var.contract.tags, { Name = "${var.contract.name}-public-${each.key}" })
}
resource "aws_internet_gateway" "portal" {
  vpc_id = aws_vpc.portal.id
  tags   = merge(var.contract.tags, { Name = "${var.contract.name}-igw" })
}
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.portal.id
  tags   = merge(var.contract.tags, { Name = "${var.contract.name}-public" })
}
resource "aws_route" "internet" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.portal.id
}
resource "aws_route_table_association" "public" {
  for_each       = aws_subnet.public
  subnet_id      = each.value.id
  route_table_id = aws_route_table.public.id
}
