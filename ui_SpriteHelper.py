# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SpriteHelperRTORNZ.ui'
##
## Created by: Qt User Interface Compiler version 6.8.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
    QLayout, QMainWindow, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setWindowModality(Qt.WindowModality.NonModal)
        #MainWindow.resize(2180, 1090)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(16)
        sizePolicy.setVerticalStretch(9)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(546, 273))
        MainWindow.setMaximumSize(QSize(2180, 1090))
        MainWindow.setSizeIncrement(QSize(16, 9))
        MainWindow.setBaseSize(QSize(872, 436))
        MainWindow.setAcceptDrops(False)
        MainWindow.setWindowTitle(u"Megamix Sprite Helper")
        MainWindow.setAutoFillBackground(True)
        MainWindow.setLocale(QLocale(QLocale.English, QLocale.Europe))
        MainWindow.setAnimated(True)
        self.grid = QWidget(MainWindow)
        self.grid.setObjectName(u"grid")
        self.grid.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy1.setHorizontalStretch(16)
        sizePolicy1.setVerticalStretch(9)
        sizePolicy1.setHeightForWidth(self.grid.sizePolicy().hasHeightForWidth())
        self.grid.setSizePolicy(sizePolicy1)
        self.grid.setMinimumSize(QSize(0, 0))
        self.grid.setSizeIncrement(QSize(16, 9))
        self.grid.setBaseSize(QSize(0, 0))
        self.grid.setAutoFillBackground(False)
        self.horizontalLayout_5 = QHBoxLayout(self.grid)
        self.horizontalLayout_5.setSpacing(5)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(5, 5, 5, 5)
        self.image_grid = QGridLayout()
        self.image_grid.setSpacing(5)
        self.image_grid.setObjectName(u"image_grid")
        self.image_grid.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.image_grid.setContentsMargins(0, 0, 0, 0)
        self.ft_song_selector_preview = QLabel(self.grid)
        self.ft_song_selector_preview.setObjectName(u"ft_song_selector_preview")
        sizePolicy1.setHeightForWidth(self.ft_song_selector_preview.sizePolicy().hasHeightForWidth())
        self.ft_song_selector_preview.setSizePolicy(sizePolicy1)
        self.ft_song_selector_preview.setMinimumSize(QSize(256, 144))
        self.ft_song_selector_preview.setMaximumSize(QSize(1920, 1080))
        self.ft_song_selector_preview.setSizeIncrement(QSize(16, 9))
        self.ft_song_selector_preview.setBaseSize(QSize(640, 360))
        self.ft_song_selector_preview.setScaledContents(True)

        self.image_grid.addWidget(self.ft_song_selector_preview, 0, 1, 1, 1)

        self.mm_result_preview = QLabel(self.grid)
        self.mm_result_preview.setObjectName(u"mm_result_preview")
        sizePolicy1.setHeightForWidth(self.mm_result_preview.sizePolicy().hasHeightForWidth())
        self.mm_result_preview.setSizePolicy(sizePolicy1)
        self.mm_result_preview.setMinimumSize(QSize(256, 144))
        self.mm_result_preview.setMaximumSize(QSize(1920, 1080))
        self.mm_result_preview.setSizeIncrement(QSize(16, 9))
        self.mm_result_preview.setBaseSize(QSize(640, 360))
        self.mm_result_preview.setScaledContents(True)

        self.image_grid.addWidget(self.mm_result_preview, 0, 0, 1, 1)

        self.ft_result_preview = QLabel(self.grid)
        self.ft_result_preview.setObjectName(u"ft_result_preview")
        sizePolicy1.setHeightForWidth(self.ft_result_preview.sizePolicy().hasHeightForWidth())
        self.ft_result_preview.setSizePolicy(sizePolicy1)
        self.ft_result_preview.setMinimumSize(QSize(256, 144))
        self.ft_result_preview.setMaximumSize(QSize(1920, 1080))
        self.ft_result_preview.setSizeIncrement(QSize(16, 9))
        self.ft_result_preview.setBaseSize(QSize(640, 360))
        self.ft_result_preview.setScaledContents(True)

        self.image_grid.addWidget(self.ft_result_preview, 1, 1, 1, 1)

        self.mm_song_selector_preview = QLabel(self.grid)
        self.mm_song_selector_preview.setObjectName(u"mm_song_selector_preview")
        sizePolicy1.setHeightForWidth(self.mm_song_selector_preview.sizePolicy().hasHeightForWidth())
        self.mm_song_selector_preview.setSizePolicy(sizePolicy1)
        self.mm_song_selector_preview.setMinimumSize(QSize(256, 144))
        self.mm_song_selector_preview.setMaximumSize(QSize(1920, 1680))
        self.mm_song_selector_preview.setSizeIncrement(QSize(16, 9))
        self.mm_song_selector_preview.setBaseSize(QSize(640, 360))
        self.mm_song_selector_preview.setScaledContents(True)

        self.image_grid.addWidget(self.mm_song_selector_preview, 1, 0, 1, 1)

        self.image_grid.setRowStretch(0, 2)
        self.image_grid.setRowStretch(1, 2)
        self.image_grid.setColumnStretch(0, 2)
        self.image_grid.setColumnStretch(1, 2)
        self.image_grid.setColumnMinimumWidth(1, 256)
        self.image_grid.setRowMinimumHeight(1, 144)

        self.horizontalLayout_5.addLayout(self.image_grid)

        self.load_buttons_box = QVBoxLayout()
        self.load_buttons_box.setSpacing(5)
        self.load_buttons_box.setObjectName(u"load_buttons_box")
        self.load_buttons_box.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.load_buttons_box_row1 = QHBoxLayout()
        self.load_buttons_box_row1.setSpacing(5)
        self.load_buttons_box_row1.setObjectName(u"load_buttons_box_row1")
        self.load_background_button = QPushButton(self.grid)
        self.load_background_button.setObjectName(u"load_background_button")

        self.load_buttons_box_row1.addWidget(self.load_background_button)

        self.load_logo_button = QPushButton(self.grid)
        self.load_logo_button.setObjectName(u"load_logo_button")

        self.load_buttons_box_row1.addWidget(self.load_logo_button)


        self.load_buttons_box.addLayout(self.load_buttons_box_row1)

        self.load_buttons_box_row2 = QHBoxLayout()
        self.load_buttons_box_row2.setSpacing(5)
        self.load_buttons_box_row2.setObjectName(u"load_buttons_box_row2")
        self.load_thumbnail_button = QPushButton(self.grid)
        self.load_thumbnail_button.setObjectName(u"load_thumbnail_button")

        self.load_buttons_box_row2.addWidget(self.load_thumbnail_button)

        self.load_jacket_button = QPushButton(self.grid)
        self.load_jacket_button.setObjectName(u"load_jacket_button")

        self.load_buttons_box_row2.addWidget(self.load_jacket_button)


        self.load_buttons_box.addLayout(self.load_buttons_box_row2)

        self.load_buttons_box_row3 = QHBoxLayout()
        self.load_buttons_box_row3.setSpacing(5)
        self.load_buttons_box_row3.setObjectName(u"load_buttons_box_row3")
        self.copy_to_clipboard_button = QPushButton(self.grid)
        self.copy_to_clipboard_button.setObjectName(u"copy_to_clipboard_button")

        self.load_buttons_box_row3.addWidget(self.copy_to_clipboard_button)


        self.load_buttons_box.addLayout(self.load_buttons_box_row3)

        self.load_buttons_box_spacer = QSpacerItem(52, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.load_buttons_box.addItem(self.load_buttons_box_spacer)


        self.horizontalLayout_5.addLayout(self.load_buttons_box)

        MainWindow.setCentralWidget(self.grid)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        self.ft_song_selector_preview.setText("")
        self.mm_result_preview.setText("")
        self.ft_result_preview.setText("")
        self.mm_song_selector_preview.setText("")
        self.load_background_button.setText(QCoreApplication.translate("MainWindow", u"Load Background", None))
        self.load_logo_button.setText(QCoreApplication.translate("MainWindow", u"Load Logo", None))
        self.load_thumbnail_button.setText(QCoreApplication.translate("MainWindow", u"Load Thumbnail", None))
        self.load_jacket_button.setText(QCoreApplication.translate("MainWindow", u"Load Jacket", None))
        self.copy_to_clipboard_button.setText(QCoreApplication.translate("MainWindow", u"Copy to clipboard", None))
        pass
    # retranslateUi

