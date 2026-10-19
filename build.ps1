param([string]$Python = 'python', [ValidateSet('onefile','portable')][string]$Kind = 'onefile')
$ErrorActionPreference='Stop'
Push-Location $PSScriptRoot
$previousKind=$env:V1_BUILD_KIND
try {
    & (Join-Path $PSScriptRoot 'scripts\fetch-dependencies.ps1')
    & $Python -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw 'Tests failed' }
    $env:V1_BUILD_KIND=$Kind
    & $Python -m PyInstaller --noconfirm --distpath "build/$Kind" --workpath "build/work-$Kind" VelocityOneMapper.spec
    if ($LASTEXITCODE -ne 0) { throw 'Build failed' }
    Write-Host "Built $Kind under build/$Kind. Windows 11 x64 and Microsoft VC++ x64 runtime are prerequisites."
} finally { $env:V1_BUILD_KIND=$previousKind;Pop-Location }
