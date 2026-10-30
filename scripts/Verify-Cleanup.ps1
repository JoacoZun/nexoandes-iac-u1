param([Parameter(Mandatory=$true)][string]$InventoryPath)
$ErrorActionPreference = 'Stop'
# Solo lectura. El inventario debe conservarse ANTES del destroy autorizado.
$inventory = Get-Content -LiteralPath $InventoryPath -Raw | ConvertFrom-Json
$region = $inventory.region
$raw = & aws ec2 describe-instances --filters "Name=instance-id,Values=$($inventory.instance_id)" --region $region --output json
if($LASTEXITCODE -ne 0){throw 'Cannot independently query instance cleanup'}
$instances = @((($raw | ConvertFrom-Json).Reservations).Instances | Where-Object { $_ })
if(@($instances | Where-Object {$_.State.Name -ne 'terminated'}).Count){throw 'EC2 not terminated'}
$queries = @(
    @('describe-vpcs','vpc-id',$inventory.vpc_id,'Vpcs'),
    @('describe-subnets','subnet-id',$inventory.subnet_id,'Subnets'),
    @('describe-security-groups','group-id',$inventory.security_group_id,'SecurityGroups'),
    @('describe-volumes','volume-id',$inventory.root_volume_id,'Volumes')
)
foreach($query in $queries){
    $raw = & aws ec2 $query[0] --filters "Name=$($query[1]),Values=$($query[2])" --region $region --output json
    if($LASTEXITCODE -ne 0){throw "Cannot query $($query[0])"}
    $data = $raw | ConvertFrom-Json
    if(@($data.($query[3])).Count -gt 0){throw "Resource remains: $($query[2])"}
}
Write-Output "PASS: independent cleanup of EC2, VPC, subnet, SG and root EBS at $((Get-Date).ToUniversalTime().ToString('o'))"
