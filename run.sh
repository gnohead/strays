#!/bin/bash

current_branch=$(git rev-parse --abbrev-ref HEAD)

if [[ $current_branch == "dev" ]]; then
    echo "development mode..."
else
    echo "service mode..."
fi

echo "done."