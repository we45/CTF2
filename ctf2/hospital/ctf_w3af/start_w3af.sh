#!/bin/bash

source /tools/w3af/venv/bin/activate && nohup /tools/w3af/w3af_api 0.0.0.0:5000 > /dev/null 2>&1 &
echo "Should have started w3af by now..."