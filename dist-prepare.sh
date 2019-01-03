#!/bin/bash
PYTHON3_PATH=?

virtualenv -p $PYTHON3_PATH env
source env/bin/activate
pip install -r requirements.txt 
mkdir dist

