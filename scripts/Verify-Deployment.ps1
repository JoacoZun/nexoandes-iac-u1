param(
    [Parameter(Mandatory=$true)][string]$Region,
    [Parameter(Mandatory=$true)][string]$PortalMarker
)
$ErrorActionPreference = 'Stop'
# Solo lectura: ejecutar DESPUÉS de un apply aprobado con el mismo backend inicializado.
$raw = & terraform output -json
if($LASTEXITCODE -ne 0){throw 'terraform output failed'}
$out = $raw | ConvertFrom-Json
$id = $out.instance_id.value
$ip = $out.public_ip.value
if($id -notmatch '^i-[0-9a-f]+$' -or $ip -notmatch '^\d+\.\d+\.\d+\.\d+$'){throw 'Invalid outputs'}
$raw = & aws ec2 describe-instances --instance-ids $id --region $Region --output json
if($LASTEXITCODE -ne 0){throw 'Independent AWS query failed'}
$instance = ($raw | ConvertFrom-Json).Reservations.Instances | Select-Object -First 1
if($instance.InstanceId -ne $id -or $instance.PublicIpAddress -ne $ip -or
   $instance.State.Name -ne 'running' -or $instance.VpcId -ne $out.vpc_id.value -or
   $instance.SubnetId -ne $out.subnet_id.value -or
   $instance.SecurityGroups.GroupId -notcontains $out.security_group_id.value -or
   $instance.MetadataOptions.HttpTokens -ne 'required'){throw 'AWS and Terraform do not match'}
New-Item -ItemType Directory -Force artifacts/verification | Out-Null
$curl = if(Get-Command curl.exe -ErrorAction SilentlyContinue){'curl.exe'}else{'curl'}
$ok = $false
for($attempt=0; $attempt -lt 30; $attempt++) {
    $status = & $curl --silent --show-error --max-time 10 --output artifacts/verification/portal.html --write-out '%{http_code}' "http://$ip/"
    if($LASTEXITCODE -eq 0 -and $status -eq '200') {
        $body = Get-Content artifacts/verification/portal.html -Raw
        if($body.Contains($PortalMarker)) { $ok = $true; break }
    }
    Start-Sleep -Seconds 10
}
if(-not $ok){throw 'Portal did not return HTTP 200 with the official expected marker'}
[pscustomobject]@{
    utc=(Get-Date).ToUniversalTime().ToString('o'); region=$Region
    instance_id=$id; public_ip=$ip; vpc_id=$out.vpc_id.value
    subnet_id=$out.subnet_id.value; security_group_id=$out.security_group_id.value
    root_volume_id=$out.root_volume_id.value; http_status=200
    body_sha256=(Get-FileHash artifacts/verification/portal.html -Algorithm SHA256).Hash
    aws_instance=$instance
} | ConvertTo-Json -Depth 20 | Set-Content artifacts/verification/inventory.json -Encoding utf8
Write-Output 'PASS: AWS identity, IP, VPC, subnet, SG, IMDSv2 and HTTP 200 with official content marker'
