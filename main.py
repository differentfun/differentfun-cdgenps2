# main.py
"""Bootstrap dell'applicazione Different Fun CDGenPS2.
Avvia la GUI definita in gui.py.
"""

import sys
from PySide6.QtWidgets import QApplication

from gui import CDGenPS2


def main() -> None:
    app = QApplication(sys.argv)
    window = CDGenPS2()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
