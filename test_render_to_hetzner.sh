#!/bin/bash


echo "Testing Render Connection to Hetznet DB"
python hetzner_connection_test_from_render.py
if [ $? -ne 0 ]; then
    echo "hetzner_connection_test_from_render.py failed"
    exit 1
fi