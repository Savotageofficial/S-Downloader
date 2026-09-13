param([string]$Python = 'python', [string]$Npm = 'npm.cmd')
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
function Run-Checked([string]$Program, [string[]]$Arguments) {
    & $Program @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Program failed with exit code $LASTEXITCODE" }
}
if (!(Test-Path '.venv\Scripts\python.exe')) {
    Run-Checked $Python @('-m', 'venv', '.venv')
}
$runtime = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
Run-Checked $runtime @('-m', 'pip', 'install', '-r', 'requirements-lock.txt')
Push-Location frontend
try {
    if (Test-Path 'package-lock.json') { Run-Checked $Npm @('ci') }
    else { Run-Checked $Npm @('install') }
    Run-Checked $Npm @('run', 'build')
} finally { Pop-Location }
New-Item -ItemType Directory -Force vendor | Out-Null
$nodePath = (Get-Command node.exe -ErrorAction Stop).Source
Copy-Item -LiteralPath $nodePath -Destination vendor\node.exe -Force
$nodeVersion = (& $nodePath --version).Trim()
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/nodejs/node/$nodeVersion/LICENSE" -OutFile vendor\NODE-LICENSE.txt
Copy-Item frontend\node_modules\react\LICENSE vendor\REACT-LICENSE.txt -Force
Copy-Item frontend\node_modules\react-dom\LICENSE vendor\REACT-DOM-LICENSE.txt -Force
Run-Checked $runtime @('collect_licenses.py')
Run-Checked $runtime @('-m', 'unittest', 'discover', '-s', 'tests', '-v')
Run-Checked $runtime @('-m', 'PyInstaller', '--noconfirm', '--clean', '--windowed', '--name', 'S-Downloader', '--add-data', 'ui;ui', '--add-data', 'vendor;vendor', '--add-data', 'THIRD-PARTY-NOTICES.md;.', '--collect-all', 'yt_dlp', '--collect-all', 'yt_dlp_ejs', 'main.py')
$smokeResult = Join-Path $PSScriptRoot 'dist\self-test.json'
Run-Checked $runtime @('-c', 'import subprocess,sys; subprocess.run([sys.argv[1], "--self-test", sys.argv[2]], check=True, timeout=60)', (Join-Path $PSScriptRoot 'dist\S-Downloader\S-Downloader.exe'), $smokeResult)
Copy-Item README.md dist\S-Downloader\README.md -Force
Copy-Item THIRD-PARTY-NOTICES.md dist\S-Downloader\THIRD-PARTY-NOTICES.md -Force
Compress-Archive -Path dist\S-Downloader -DestinationPath dist\S-Downloader-Windows-x64.zip -Force
Write-Host 'Ready: dist\S-Downloader-Windows-x64.zip'
