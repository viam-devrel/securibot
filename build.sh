#!/usr/bin/env bash

cd $(dirname $0)

# Create a virtual environment to run our code
VENV_NAME=".venv-build"
PYTHON="$VENV_NAME/bin/python"

export PATH=$PATH:$HOME/.local/bin

source $VENV_NAME/bin/activate

if ! uv pip install pyinstaller; then
  exit 1
fi

uv run pyinstaller --onefile -p src src/main.py
tar -czvf dist/archive.tar.gz ./dist/main meta.json
