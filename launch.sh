#!/bin/bash

# Student Engagement Tracker - Launch Script

echo "============================================================"
echo "  STUDENT ENGAGEMENT TRACKING SYSTEM"
echo "============================================================"
echo ""
echo "Starting application..."
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null
then
    echo "Error: Streamlit is not installed."
    echo "Please run: pip install -r requirements.txt"
    exit 1
fi

# Launch the application
streamlit run app.py

echo ""
echo "Application stopped."
echo "============================================================"
