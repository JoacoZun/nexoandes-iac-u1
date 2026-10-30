param([string]$Terraform = 'terraform')
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
New-Item -ItemType Directory -Force artifacts/checks | Out-Null
$results = @()
function Invoke-Control([string]$Name, [string]$Exe, [string[]]$Arguments) {
    if (-not (Get-Command $Exe -ErrorAction SilentlyContinue)) {
        $script:results += [pscustomobject]@{ control=$Name; status='NOT_RUN'; reason="Missing executable: $Exe" }
        return
    }
    # Windows PowerShell 5 convierte stderr nativo en ErrorRecord aunque exit sea 0.
    $ErrorActionPreference = 'Continue'
    & $Exe @Arguments 2>&1 | Tee-Object -FilePath "artifacts/checks/$Name.log" | Out-Host
    $code = $LASTEXITCODE
    $ErrorActionPreference = 'Stop'
    $script:results += [pscustomobject]@{ control=$Name; status=$(if($code -eq 0){'PASS'}else{'FAIL'}); exit_code=$code }
}
Invoke-Control 'init' $Terraform @('init','-backend=false','-input=false','-lockfile=readonly','-no-color')
Invoke-Control 'format' $Terraform @('fmt','-check','-recursive','-no-color')
Invoke-Control 'validate' $Terraform @('validate','-no-color')
Invoke-Control 'test' $Terraform @('test','-no-color')
$lint = if(Test-Path '.tools/tflint/tflint.exe'){'.tools/tflint/tflint.exe'}else{'tflint'}
$env:TFLINT_PLUGIN_DIR = Join-Path (Get-Location) '.tools/tflint-plugins'
Invoke-Control 'lint-init' $lint @('--init')
$lintConfig = Join-Path $PWD '.tflint.hcl'
Invoke-Control 'lint' $lint @('--recursive','--max-workers=1',"--config=$lintConfig")
$python = if(Test-Path '.venv/Scripts/python.exe'){'.venv/Scripts/python.exe'}elseif(Test-Path '.tools/python/python.exe'){'.tools/python/python.exe'}else{'python'}
# Checkov 3.2.495 conserva su Python 3.12; su fork hcl2 no se mezcla con .venv.
$scannerPython = if(Test-Path '.tools/python/python.exe'){'.tools/python/python.exe'}else{$python}
Invoke-Control 'security' $scannerPython @('-m','checkov.main','--config-file','.checkov.yml')
Invoke-Control 'python-tests' $python @('-m','unittest','discover','-s','tests','-p','test_*.py','-v')
Invoke-Control 'repository' $python @('scripts/check_repository.py')
[pscustomobject]@{ utc=(Get-Date).ToUniversalTime().ToString('o'); results=$results } |
    ConvertTo-Json -Depth 5 | Set-Content artifacts/checks/results.json -Encoding utf8
if ($results.status -contains 'FAIL' -or $results.status -contains 'NOT_RUN') { exit 1 }
