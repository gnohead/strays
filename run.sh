#!/bin/bash

current_branch=$(git rev-parse --abbrev-ref HEAD)

if [[ $current_branch == "dev" ]]; then
    streamlit run ./app/app_irp_agent.py \
        --server.address=172.21.0.2 

else
    streamlit run ./app/app_irp_agent.py \
        --server.address=172.21.0.2 
fi

echo "done."