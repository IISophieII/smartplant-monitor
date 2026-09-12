$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$venvPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $venvPython)) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    $bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    if ($pythonCommand) {
        $basePython = $pythonCommand.Source
    } elseif (Test-Path $bundledPython) {
        $basePython = $bundledPython
    } else {
        throw 'Install Python 3.13 and add it to PATH, then run this script again.'
    }
    & $basePython -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Could not create Python environment.' }
}
& $venvPython -m pip install -e '.[dev]'
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
Write-Host 'Open http://127.0.0.1:8000 in your browser. Press Ctrl+C to stop.'
& $venvPython -m uvicorn smartplant.app:app --host 127.0.0.1 --port 8000
