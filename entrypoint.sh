#!/bin/bash

# Navigate to the directory containing your Makefile
cd /Users/luiscruz/Desktop/projects/strava-analysis/ || exit 1

# Run make
uv run python main.py
