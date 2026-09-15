param(
    [string]$Version = '1.0.1',
    [string]$Compiler = ''
)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if ($Version -notmatch '^\d+\.\d+\.\d+(\.\d+)?$') { throw 'Version must be numeric, e.g. 1.0.0.' }
if (!(Test-Path 'dist\S-Downloader\S-Downloader.exe')) { throw 'Run build.ps1 first.' }
Copy-Item README.md,THIRD-PARTY-NOTICES.md,VALIDATION.md -Destination dist\S-Downloader -Force
if (!$Compiler) {
    $candidates = @(
        'build\installer-tools\InnoSetup\ISCC.exe',
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
    )
    $Compiler = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
}
if (!$Compiler) { throw 'Install Inno Setup 6 or pass -Compiler with the path to ISCC.exe.' }
New-Item -ItemType Directory -Force build\installer-tools | Out-Null
$bootstrap = Join-Path $PSScriptRoot 'build\installer-tools\MicrosoftEdgeWebview2Setup.exe'
if (!(Test-Path $bootstrap)) {
    Invoke-WebRequest 'https://go.microsoft.com/fwlink/p/?LinkId=2124703' -OutFile $bootstrap
}
$signature = Get-AuthenticodeSignature -LiteralPath $bootstrap
if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch 'O=Microsoft Corporation') {
    throw 'The WebView2 bootstrapper must have a valid Microsoft signature.'
}
& $Compiler "/DAppVersion=$Version" 'installer\S-Downloader.iss'
if ($LASTEXITCODE -ne 0) { throw "Installer compilation failed: $LASTEXITCODE" }
$installer = Join-Path $PSScriptRoot "dist\S-Downloader-Setup-$Version-x64.exe"
$hash = (Get-FileHash -LiteralPath $installer -Algorithm SHA256).Hash
"$hash  $(Split-Path $installer -Leaf)" | Set-Content "$installer.sha256" -Encoding ascii
Write-Output "Ready: $installer"
