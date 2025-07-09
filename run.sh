#!/bin/bash
# Papercraft Automation Runner Script

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the main script
python main.py "$@"
