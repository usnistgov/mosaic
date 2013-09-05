#!/bin/sh

# $1=coderoot

export PYTHONPATH=$1:$1/dependencies/lib/python2.7/site-packages:$PYTHONPATH

cd $1
python analysisScript.py
rm analysisScript.py
