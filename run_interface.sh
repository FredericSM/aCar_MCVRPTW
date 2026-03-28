#!/bin/bash
# Start the MCVRPTW Heuristic Solver Web Interface

# Detect Python 3
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

echo "Using Python: $($PYTHON --version)"

# Check if Python virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating Python virtual environment..."
    $PYTHON -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install/update requirements
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Start Streamlit app
echo ""
echo "🚀 Starting MCVRPTW Heuristic Solver Web Interface..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📱 Open your browser and go to:"
echo "    http://localhost:8501"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
$PYTHON -m streamlit run interface.py

