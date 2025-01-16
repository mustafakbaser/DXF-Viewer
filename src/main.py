import sys
from PyQt6.QtWidgets import QApplication
from viewer import DXFViewer

def main():
    app = QApplication(sys.argv)
    viewer = DXFViewer()
    viewer.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 