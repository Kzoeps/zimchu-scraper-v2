#!/bin/bash

cd /home/kzoeps/Projects/zimchu/zimchu-scraper-v2

echo "=== Main script started at $(date) ===" >> main_errors.log
source venv/bin/activate
export RUN_HEADLESS=True
python main.py

echo "=== Main script completed at $(date) ===" >> main_errors.log
deactivate
