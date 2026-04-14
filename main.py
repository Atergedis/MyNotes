import sys
from PySide6.QtWidgets import QApplication
from MainWindow import MainWindow 
 
def main():
        app = QApplication(sys.argv)
        app.setApplicationName("VeryCoolNotes")
        app.setApplicationVersion("0.1")
        app.setOrganizationName("Atergedis")

        window = MainWindow()
        window.show()
        sys.exit(app.exec())

if __name__ == "__main__":
    main()