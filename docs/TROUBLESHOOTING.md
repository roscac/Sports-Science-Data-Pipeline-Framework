# Troubleshooting

## GUI does not open
- Ensure setup has been run:
```bash
python scripts/first_time_setup.py
```
- Ensure you are running from the project root
- The GUI auto-reexecs into `.venv` if it exists

## ModuleNotFoundError
Use:
```bash
python -m gui.main_window
```

## PySide6 not found
Dependencies are installed via:
```bash
pip install -r requirements.txt
```

## Advanced tools not visible
- Toggle **Advanced Mode** in the GUI to reveal extra tools
- Restart the GUI after updating code

## Still stuck?
This is a demonstration project; errors are typically environment-related.
Reviewers are encouraged to inspect the code structure rather than execute it fully.
