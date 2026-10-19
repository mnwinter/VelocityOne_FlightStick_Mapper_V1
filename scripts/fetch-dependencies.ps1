param([string]$Destination = (Join-Path $PSScriptRoot '..\backend'))
$ErrorActionPreference = 'Stop'
$dependencyRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$dependencies = Get-Content (Join-Path $dependencyRoot 'dependencies.lock.json') -Raw | ConvertFrom-Json
New-Item -ItemType Directory -Path $Destination -Force | Out-Null
foreach ($dependency in $dependencies) {
    $target = Join-Path $Destination $dependency.file
    if (-not (Test-Path -LiteralPath $target) -or (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant() -ne $dependency.sha256) {
        $temporary = "$target.download"
        try {
            Invoke-WebRequest -Uri $dependency.url -OutFile $temporary -UseBasicParsing
            if ((Get-FileHash -LiteralPath $temporary -Algorithm SHA256).Hash.ToLowerInvariant() -ne $dependency.sha256) { throw "Hash mismatch: $($dependency.file)" }
            Move-Item -LiteralPath $temporary -Destination $target -Force
        } finally { if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary } }
    }
    if ($dependency.authenticode -and (Get-AuthenticodeSignature -LiteralPath $target).Status -ne 'Valid') { throw "Signature validation failed: $($dependency.file)" }
    Write-Host "Verified $($dependency.file)"
}
