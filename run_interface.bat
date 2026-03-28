@echo off
REM Start the MCVRPTW Heuristic Solver Web Interface (Windows)

REM Check if Python virtual environment exists
if not exist ".venv" (
    echo Creating Python virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install/update requirements
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Start Streamlit app
echo Starting MCVRPTW Heuristic Solver Interface...
echo The app will open in your browser at http://localhost:8501
echo.
streamlit run interface.py
