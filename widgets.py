import time
from enum import Enum
from threading import Lock

from pyqt_advanced_slider import Slider

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt, Signal, QTimer)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform, QMouseEvent)
from PySide6.QtWidgets import (QAbstractScrollArea, QAbstractSpinBox, QApplication, QCheckBox,
                               QDoubleSpinBox, QFrame, QGridLayout, QHBoxLayout,
                               QLabel, QLayout, QMainWindow, QPushButton,
                               QScrollArea, QSizePolicy, QSpacerItem, QSpinBox,
                               QVBoxLayout, QWidget, QScrollBar, QSlider)
from superqt import QDoubleSlider
from superqt.utils import qdebounced, qthrottled


class QLabel_clickable(QLabel):
    clicked=Signal()

    def mousePressEvent(self, ev):
        self.clicked.emit()

class Stylesheet(Enum):
    SCROLL_AREA_CONFLICT = ".QScrollArea {border: 1px solid rgb(235,51,101);border-radius: 2px;}"
    SCROLL_AREA_UNFILLED = ".QScrollArea {border: 1px solid rgb(171,237,253);border-radius: 2px;}"
    ID_FIELD_CONFLICT = ".PlaceholderDoubleSpinBox {color: rgb(235,51,101);}"
    ID_FIELD_PLACEHOLDER = ".PlaceholderDoubleSpinBox {color: rgb(155,155,155);}"

class PlaceholderDoubleSpinBox(QDoubleSpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workaround = True
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, event, /):
        if self.hasFocus():
            QSpinBox.wheelEvent(self, event)

    def focusInEvent(self, event):
        #TODO do it properly // Shitty workaround for setupUi being executed bit later than init
        if self.workaround:
            self.setSpecialValueText(self.specialValueText())
            self.setPlaceholderText(self.specialValueText())
            self.workaround = False

        if self.value() == self.minimum():
            self.setSpecialValueText("")
        super().focusInEvent(event)
        QTimer.singleShot(10, self.selectAll)


    def focusOutEvent(self, event):
        if self.value() == self.minimum():
            self.setSpecialValueText(self.placeholderText())
        super().focusOutEvent(event)

    def setPlaceholderText(self, text):
        self._placeholder_text = text
        self.setSpecialValueText(text)

    def placeholderText(self):
        return getattr(self, '_placeholder_text', "")


class EditableDoubleLabel(QWidget):
    editingFinished = Signal()

    def __init__(self, initial_value=0,sprite=None,setting=None,decimals=0, rough_step=1,precise_step=1, range=(0,1), parent=None):
        super().__init__(parent)
        self.initial_value = initial_value
        self.value = initial_value
        self.decimals = decimals
        self.block_drawing = False
        self.block_editing = False
        self.setFixedSize(160, 75)

        self.editable_label_size = QSize(160,30)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)


        font1 = QFont()
        font1.setFamilies([u"Nimbus Sans Narrow [UKWN]"])
        font1.setPointSize(9)
        font1.setBold(False)
        font1.setKerning(True)

        self.info_label = QLabel()
        self.info_label.setText(f"{sprite.type.value + " " + setting.value}")
        self.info_label.setFont(font1)

        self.label = QLabel()
        self.label.setCursor(Qt.CursorShape.IBeamCursor)
        self.label.setText(f"{self.value:.{self.decimals}f}")
        self.label.setMinimumSize(self.editable_label_size)
        self.label.mousePressEvent = self.on_label_clicked

        self.spinbox = QDoubleSpinBox()
        self.spinbox.setValue(self.value)
        self.spinbox.setDecimals(self.decimals)
        self.spinbox.setSingleStep(precise_step)
        self.spinbox.setMinimumSize(self.editable_label_size)
        #self.spinbox.editingFinished.connect(self.finish_editing)
        self.spinbox.valueChanged.connect(self.sync_slider)

        self.slider = QDoubleSlider(Qt.Horizontal)
        self.slider.setPageStep(rough_step)
        self.slider.setSingleStep(rough_step)
        #self.slider.sliderReleased.connect(self.slider_editing_finish)
        self.slider.valueChanged.connect(self.slider_value_changed)

        self.set_range(range)

        self.layout.addWidget(self.info_label)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.spinbox)
        self.layout.addWidget(self.slider)



        self.label.setVisible(True)
        self.spinbox.setVisible(False)

    def on_label_clicked(self, event: QMouseEvent):
        if self.block_editing:
            pass
        else:
            if event.button() == Qt.MouseButton.LeftButton:
                self.start_editing()

    def start_editing(self):

        self.label.setVisible(False)
        self.spinbox.setVisible(True)
        self.spinbox.setFocus()
        self.spinbox.selectAll()

        self.spinbox.installEventFilter(self)

    def finish_editing(self):

        if self.decimals == 0:
            self.value = int(self.spinbox.value())
        else:
            self.value = self.spinbox.value()

        self.label.setText(f"{self.value:.{self.decimals}f}")
        self.slider.setValue(self.value)
        self.spinbox.setVisible(False)
        self.label.setVisible(True)
        self.spinbox.removeEventFilter(self)

        if self.block_editing:
            self.spinbox.setDisabled(True)
        else:
            self.spinbox.setDisabled(False)

        if not self.block_drawing:
            self.editingFinished.emit()

    def slider_editing_finish(self):
        if self.decimals == 0:
            self.value = int(self.slider.value())
        else:
            self.value = self.slider.value()

        self.label.setText(f"{self.value:.{self.decimals}f}")
        self.spinbox.setValue(self.value)

        if not self.block_drawing:
            self.editingFinished.emit()

    def slider_value_changed(self):
        if not self.block_editing:
            self.value = self.slider.value()
            self.label.setText(f"{self.value:.{self.decimals}f}")
            self.spinbox.setValue(self.value)
            qthrottled(self.slider_editing_finish(),timeout=20)

    def sync_slider(self):
        self.slider.setValue(self.spinbox.value())

    def set_range(self,range):
        minimum = range[0]
        maximum = range[1]

        self.spinbox.setMinimum(minimum)
        self.spinbox.setMaximum(maximum)

        self.slider.setMinimum(minimum)
        self.slider.setMaximum(maximum)

        range = maximum - minimum

        if int(range == 0) and int(range == 0):
            self.block_editing = True
            self.label.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            self.block_editing = False
            self.label.setCursor(Qt.CursorShape.IBeamCursor)

    def eventFilter(self, obj, event):
        if obj == self.spinbox and event.type() == event.Type.FocusOut:
            QTimer.singleShot(100, self.finish_editing)
        return super().eventFilter(obj, event)

    def setValue(self, value):
        self.value = value
        self.label.setText(f"{value:.{self.decimals}f}")
        self.spinbox.setValue(self.value)
        self.slider.setValue(self.value)

    def getValue(self):
        return self.value

    def reset_value(self):
        self.setValue(self.initial_value)
