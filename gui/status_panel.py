"""Minimal status log widget."""
from PySide6.QtWidgets import QTextEdit

class StatusPanel(QTextEdit):
    def __init__(self):
        super().__init__(); self.setReadOnly(True)
    def log(self, msg: str):
        """Append a log line to the panel."""
        self.append(msg)
