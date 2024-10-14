#!/bin/bash
# virtualenv를 이용한 python 환경 설정
#
# bash 에서 쉘 앞에 환경이 표시되지 않으면 `.bashrc` 파일에 다음 내용을 추가
# ```
# if ! [ -z ${VIRTUAL_ENV_PROMPT} ]; then
#     PS1="(${VIRTUAL_ENV_PROMPT}) ${PS1-}"
#     export PS1
# fi
# ```
#


platform=$(uname)
if [[ ${platform} == "Darwin" ]]; then
    pyexec="python3.11"
else
    pyexec="python3"
fi

verstr=$(${pyexec} --version | sed -E 's/Python ([0-9]+\.[0-9]+)\.[0-9]+/\1/')

cwd=$(pwd)
vernum=$(echo "${verstr}" | sed "s/\.//g")
pypath=$(whereis python${verstr} | awk '{print $2}')
venvpath="${cwd}/_py$(echo "${vernum}")_"
reqfile="${cwd}/requirements.txt"
ignorefile="${cwd}/.gitignore"
env_variables="${cwd}/env.conf"

function regist_env_variables() {
    # env.ini 에 설정된 환경 변수 로드
    # 마지막 줄에 개행문자가 없어도 읽을 수 있도록 `-r` 옵션 추가
    while IFS='=' read -r key value || [[ -n $key ]] 
    do
        # 주석 및 섹션 건너뛰기
        if [[ $key == \#* ]] || [[ -z $value ]] || [[ -z $key ]]; then
            continue
        fi

        # 환경변수에 등록
        export $key=$value
        echo "$key=${!key}"

    done < $env_variables
}


function activate_env() {
    (
        # 환경 진입
        source "${venvpath}/bin/activate"
        export PYTHONPATH="$PYTHONPATH:${cwd}"

        # 환경 변수 로드
        if [ -f "$env_variables" ]; then
            regist_env_variables
        else
            echo "No env_variables file: ${env_variables}"
        fi

        # 명령(인자 실행)
        $@

        # 환경 종료
        deactivate
    )
}


function remove_unnecessary_files() {
    while IFS= read -r line
    do
        # 주석 및 빈 줄 건너뛰기
        [[ "$line" =~ ^#.*$ ]] && continue
        [[ -z "$line" ]] && continue

        # 명시된 파일 패턴에 맞는 파일/폴더 삭제
        echo "> Removing '$line'..."
        find . -name "$line" -exec rm -rfv {} \;
    done < $ignorefile
}


function run_pytest() {
    activate_env pytest -v -s
}


function run_runlist() {
    activate_env python ./run.py
}


function create_env() {
    # 현재 폴더에 python 환경 생성
    if [ -z "$pypath" ]; then
        echo "No python${verstr} installed."
        exit 1
    fi

    if [ ! -d "$venvpath" ]; then
        if [[ ${platform} != "Linux" ]]; then
            ${pypath} -m pip install --upgrade pip && \
            ${pypath} -m pip install virtualenv
        fi

        ${pypath} -m virtualenv --python="${pypath}" "${venvpath}"

        # 패키지 실행 환경 설정
        if [ $? -eq 0 ]; then
            # requirements.txt 파일이 존재하면 패키지 설치
            if [ -f "${reqfile}" ]; then
                activate_env python -m pip install -r ${reqfile}
            fi
        fi
    else
        echo "$venvpath already exists."
    fi
}

function upgrade_requirements() {
    activate_env pip install --upgrade pip
    if [ -f "${reqfile}" ]; then
        activate_env python -m pip install -r ${reqfile}
    fi
}

function usage() {
    echo "Usage: $(basename $0) [create|freeze|purge|clean|test|{command}]"
    echo "  create: Create python environment"
    echo "  recreate: Re-create python environment"
    echo "  upgrade: Upgrade python requirement packages"
    echo "  freeze: Make requirements.txt file"
    echo "  activate: Enter the virtual environment shell"
    echo "  purge: Remove virtual environment and unnecessary files"
    echo "  clean: Remove unnecessary files"
    echo "  test: run pytest"
    echo "  {command}: Execute command in virtual environment"
}


# 실행
if [ "$#" -eq 0 ]; then
    usage

elif [ "$1" = "create" ]; then
    create_env

elif [ "$1" = "recreate" ]; then
    # 현재 가상환경 삭제하고 새로 생성
    rm -rfv "${venvpath}"
    create_env

elif [ "$1" = "upgrade" ]; then
    upgrade_requirements

elif [ "$1" = "freeze" ]; then
    activate_env python -m pip freeze > ${reqfile}

elif [ "$1" = "purge" ] && [ -d "${venvpath}" ]; then
    # 가상환경 삭제
    rm -rfv "${venvpath}"

    # 불필요한 파일 삭제
    if [ -f "${ignorefile}" ]; then
        remove_unnecessary_files
    fi

elif [ "$1" = "clean" ]; then
    if [ -f "${ignorefile}" ]; then
        remove_unnecessary_files
    else
        echo "No ignore file: ${ignorefile}"
    fi

elif [ "$1" = "test" ]; then
    run_pytest

elif [ "$1" = "run" ]; then
    run_runlist

elif [ "$1" = "activate" ]; then
    if [[ ${platform} == "Darwin" ]]; then
        activate_env /bin/zsh
    else
        activate_env /bin/bash
    fi

elif [ -n "$1" ]; then
    # 환경에서 명령어 실행
    activate_env $@ # 명령어 옵션과 함께 실행

else
    usage
fi


echo "'$(basename $0) $1' done."
exit 0
