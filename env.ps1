#
# virtualenv를 이용한 python 환경 설정
#
# 마이크로소프트 파워쉘 환경의 파이썬 가상환경 유틸리티
# 권한문제로 실행이 안되면, 파워쉘에서 다음 명령을 실행 
# `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
#

# 환경 변수 설정
$cwd = Get-Location
$pypath = (Get-Command python).Source
$vernum = $pypath -replace '.*Python(\d+).*', '$1'
$venvpath = Join-Path $cwd ("_py" + $vernum + "_")
$reqfile = Join-Path $cwd "requirements.txt"
$ignorefile = Join-Path $cwd ".gitignore"

function New-Environment {
    # 현재 폴더에 python 환경 생성
    if (-not (Test-Path $pypath)) {
        Write-Host "No python$verstr installed."
        exit 1
    }

    if (-not (Test-Path $venvpath)) {
        & $pypath -m pip install --upgrade pip
        & $pypath -m pip install virtualenv
        & $pypath -m virtualenv --python=$pypath $venvpath

        # 패키지 실행 환경 설정
        if ($LASTEXITCODE -eq 0) {
            Invoke-Expression "$venvpath\Scripts\activate.ps1"
            & $env:PYTHONPATH = (Get-Location).Path
            & python -m pip install pip --upgrade

            # requirements.txt 파일이 존재하면 패키지 설치
            if (Test-Path $reqfile) {
                & python -m pip install -r $reqfile
            }

            & deactivate
        }
    } else {
        Write-Host "$venvpath already exists."
    }
}

function Remove-Unnecessary {
    # .gitignore 파일에 정의된 이름을 갖는 파일을 모두 제거
    if (Test-Path $ignorefile) {
        $ignorePatterns = Get-Content $ignorefile | Where-Object { $_.Trim() -ne "" }
        foreach ($pattern in $ignorePatterns) {
            Get-ChildItem -Path $cwd -Recurse -Filter $pattern | Remove-Item -Force -Verbose -Recurse
        }
    } else {
        Write-Host ".gitignore file does not exist."
    }
}

function Remove-Environment {
        # python 가상환경 제거
        if (Test-Path $venvpath) {
            Remove-Item $venvpath -Recurse -Force -Verbose
        }   
}

function Enable-Environment {
    # 파이썬 환경에 진입
    Invoke-Expression "$venvpath\Scripts\activate.ps1"
    & $env:PYTHONPATH = (Get-Location).Path
}

function Invoke-Command {
    param($commandArgs)
    # 특정 명령어를 파이썬 환경에서 실행
    Invoke-Expression "$venvpath\Scripts\activate.ps1"
    & $env:PYTHONPATH = (Get-Location).Path
    & Invoke-Expression "$commandArgs"
    & deactivate
}

function Update-Requirements {
    Invoke-Expression "$venvpath\Scripts\activate.ps1"
    & $env:PYTHONPATH = (Get-Location).Path
    & python -m pip install --upgrade pip
    if (Test-Path $reqfile) {
        & python -m pip install -r $reqfile
    }
    & deactivate
}

# 실행
try {
    if ($args.Count -eq 0) {
        Write-Host "Usage: .\env.ps1 [create|purge|activate|{command}]"
        Write-Host "  create: Create python environment"
        Write-Host "  recreate: Re-create python environment"
        Write-Host "  upgrade: Upgrade python requirement packages"
        Write-Host "  purge: Remove virtual environment and unnecessary files"
        Write-Host "  clean: Remove unnecessary files"
        Write-Host "  activate: Activate environment shell"
        Write-Host "  ""command"": Execute command in virtual environment"
    } elseif ($args[0] -eq "create") {
        New-Environment
    } elseif ($args[0] -eq "recreate") {
        Remove-Environment
        New-Environment
    } elseif ($args[0] -eq "purge") {
        Remove-Unnecessary
        Remove-Environment
    } elseif ($args[0] -eq "upgrade") {
        Update-Requirements
    } elseif ($args[0] -eq "clean") {
        Remove-Unnecessary
    } elseif ($args[0] -eq "activate") {
        Enable-Environment
    } else {
        Invoke-Command -commandArgs $args
    }   
}
finally {   
    Write-Host "'env.ps1 $args' done."
    exit 0
}
