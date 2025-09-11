from enum import Enum

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt, Signal)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractScrollArea, QAbstractSpinBox, QApplication, QCheckBox,
    QDoubleSpinBox, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QLayout, QMainWindow, QPushButton,
    QScrollArea, QSizePolicy, QSpacerItem, QSpinBox,
    QVBoxLayout, QWidget)

class QLabel_clickable(QLabel):
    clicked=Signal()

    def mousePressEvent(self, ev):
        self.clicked.emit()

class Stylesheet(Enum):
    SCROLL_AREA_CONFLICT = ".QScrollArea {border: 1px solid rgb(255,0,0);border-radius: 2px;}"
    SCROLL_AREA_UNFILLED = ".QScrollArea {border: 1px solid rgb(255,155,155);border-radius: 2px;}"
    ID_FIELD_CONFLICT = ".QDoubleSpinBox {color: rgb(255,100,100);}"
    ID_FIELD_PLACEHOLDER = ".QDoubleSpinBox {color: rgb(155,155,155);}"