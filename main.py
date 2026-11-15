import sys
import os
import qdarktheme
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

# Fix Linux Locale GTK warnings natively inside the app
os.environ["LC_ALL"] = "C"

def main():
    app = QApplication(sys.argv)
    
    # dark theme by default
    qdarktheme.setup_theme("dark")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
