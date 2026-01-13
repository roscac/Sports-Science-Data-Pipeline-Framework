@echo off
IF NOT EXIST .venv (
  python scripts\first_time_setup.py
)
CALL .venv\Scripts\activate.bat
python gui\main_window.py
