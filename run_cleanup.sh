#!/bin/bash

# Navigate to the project directory
cd /home/kzoeps/Projects/zimchu/zimchu-scraper-v2

# Add timestamp to log
echo "=== Cleanup script started at $(date) ===" 

# Activate the virtual environment
source venv/bin/activate

# Run the cleanup script
python cleanup_listings.py

# Add completion timestamp to log
echo "=== Cleanup script completed at $(date) ===" >> cleanup_errors.log

# Deactivate the virtual environment
deactivate
