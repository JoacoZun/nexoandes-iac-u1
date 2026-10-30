param(
    [ValidatePattern('^[a-z0-9_]+$')][string]$ApellidosNombres,
    [switch]$Preview
)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$safeRoot = $root -replace '\\', '/'
Set-Location $root
$files = & git -c "safe.directory=$safeRoot" ls-files --cached --others --exclude-standard
if($LASTEXITCODE -ne 0){throw 'Cannot obtain repository file list'}
$allowed = @('.tf','.hcl','.md','.py','.ps1','.sh','.tpl','.yml','.yaml','.txt','.disabled')
$selected = @($files | Where-Object {
    $path = $_
    $parts = $path -split '/'
    ($parts.Count -eq 1 -or $parts[0] -in @('modules','templates','tests','scripts','docs','ci','.github')) -and
    ([IO.Path]::GetExtension($path) -in $allowed -or $path -in @('.gitignore','.gitattributes','terraform.tfvars.example')) -and
    $path -notmatch '(^|/)(\.git|\.terraform|\.aws|\.tools|\.venv|__pycache__)(/|$)' -and
    ($path -eq 'terraform.tfvars.example' -or
     $path -notmatch '(tfstate|\.tfvars|\.tfplan|credentials|backend\.hcl|backend\.tf|override\.tf|\.pem|\.key|\.env)')
})
if($selected -notcontains '.terraform.lock.hcl'){throw 'Provider lock file missing'}
if($Preview){ $selected; return }
if([string]::IsNullOrWhiteSpace($ApellidosNombres)){throw 'Indique los apellidos/nombres reales o use -Preview'}
New-Item -ItemType Directory -Force dist | Out-Null
$zipPath = Join-Path $root "dist/eva1_$ApellidosNombres.zip"
if(Test-Path -LiteralPath $zipPath){throw 'ZIP already exists; inspect and rename it before regenerating'}
Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [IO.Compression.ZipFile]::Open($zipPath, [IO.Compression.ZipArchiveMode]::Create)
try {
    foreach($file in $selected){
        [IO.Compression.ZipFileExtensions]::CreateEntryFromFile($archive, (Join-Path $root $file), $file) | Out-Null
    }
} finally { $archive.Dispose() }
$read = [IO.Compression.ZipFile]::OpenRead($zipPath)
try { $read.Entries.FullName | Set-Content "dist/zip-manifest.txt" -Encoding utf8 }
finally { $read.Dispose() }
Get-FileHash -LiteralPath $zipPath -Algorithm SHA256
Write-Output 'ZIP generado. Revisar manifiesto y secretos manualmente; no certifica despliegue ni ficha PDF completa.'
