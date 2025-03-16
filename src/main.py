import sys
from PyQt6.QtWidgets import QApplication
from viewer import DXFViewer
from settings import Settings

def main():
    app = QApplication(sys.argv)
    
    # Load settings
    settings = Settings()
    
    # Create and show viewer
    viewer = DXFViewer()
    viewer.show()
    
    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 