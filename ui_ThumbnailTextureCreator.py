# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Thumbnail Texture CreatorzZjzrw.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QPushButton,
    QScrollArea, QSizePolicy, QVBoxLayout, QWidget)

class Ui_ThumbnailTextureCreator(object):
    def setupUi(self, ThumbnailTextureCreator):
        if not ThumbnailTextureCreator.objectName():
            ThumbnailTextureCreator.setObjectName(u"ThumbnailTextureCreator")
        ThumbnailTextureCreator.resize(620, 299)
        ThumbnailTextureCreator.setMinimumSize(QSize(620, 0))
        self.verticalLayout = QVBoxLayout(ThumbnailTextureCreator)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.load_folder_button = QPushButton(ThumbnailTextureCreator)
        self.load_folder_button.setObjectName(u"load_folder_button")

        self.verticalLayout.addWidget(self.load_folder_button)

        self.load_image_button = QPushButton(ThumbnailTextureCreator)
        self.load_image_button.setObjectName(u"load_image_button")

        self.verticalLayout.addWidget(self.load_image_button)

        self.thumbnails_loaded_label = QLabel(ThumbnailTextureCreator)
        self.thumbnails_loaded_label.setObjectName(u"thumbnails_loaded_label")

        self.verticalLayout.addWidget(self.thumbnails_loaded_label)

        self.thumbnails_to_fillout_label = QLabel(ThumbnailTextureCreator)
        self.thumbnails_to_fillout_label.setObjectName(u"thumbnails_to_fillout_label")

        self.verticalLayout.addWidget(self.thumbnails_to_fillout_label)

        self.export_farc_button = QPushButton(ThumbnailTextureCreator)
        self.export_farc_button.setObjectName(u"export_farc_button")

        self.verticalLayout.addWidget(self.export_farc_button)

        self.scrollArea = QScrollArea(ThumbnailTextureCreator)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 608, 143))
        self.scrollAreaWidgetContents.setMinimumSize(QSize(0, 0))
        self.gridLayout = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setObjectName(u"gridLayout")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)


        self.retranslateUi(ThumbnailTextureCreator)

        QMetaObject.connectSlotsByName(ThumbnailTextureCreator)
    # setupUi

    def retranslateUi(self, ThumbnailTextureCreator):
        ThumbnailTextureCreator.setWindowTitle(QCoreApplication.translate("ThumbnailTextureCreator", u"Thumbnail Texture Creator", None))
        self.load_folder_button.setText(QCoreApplication.translate("ThumbnailTextureCreator", u"Load from folder", None))
        self.load_image_button.setText(QCoreApplication.translate("ThumbnailTextureCreator", u"Load Image", None))
        self.thumbnails_loaded_label.setText(QCoreApplication.translate("ThumbnailTextureCreator", u"Thumbnails loaded: XXX", None))
        self.thumbnails_to_fillout_label.setText(QCoreApplication.translate("ThumbnailTextureCreator", u"Thumbnails that need their ID filled out: XXX", None))
        self.export_farc_button.setText(QCoreApplication.translate("ThumbnailTextureCreator", u"Export Farc", None))
    # retranslateUi

