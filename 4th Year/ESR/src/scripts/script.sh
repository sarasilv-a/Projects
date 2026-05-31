#!/bin/bash
cd /home/core/Desktop/ESR/src || exit 1
export PYTHONPATH=/home/core/Desktop/ESR/src:$PYTHONPATH
exec "$SHELL"

