#!/usr/bin/env bash

set -e

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Environment setup complete. Run 'source venv/bin/activate' to activate the virtual environment."