#!/usr/bin/env pwsh

$existing_python_path = $env:PYTHONPATH
$current_path = (Get-Location).Path
if ($existing_python_path) {
    $env:PYTHONPATH = "$existing_python_path;$current_path"
} else {
    $env:PYTHONPATH = $current_path
}

$current_branch = git rev-parse --abbrev-ref HEAD

if ($current_branch -eq "dev") {
    Write-Output ">>>>> Running on development mode <<<<<"
} else {
    Write-Output ">>>>> Running on service mode <<<<<"
}

Write-Output "done."