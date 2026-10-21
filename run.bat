@echo off
title Intelligent Study Assistant
echo ========================================================
echo   Launching Intelligent Study Assistant (Streamlit)
echo ========================================================
cd /d "%~dp0"
python -m streamlit run app.py
pause
