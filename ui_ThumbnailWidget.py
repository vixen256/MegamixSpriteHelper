# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ThumbnailWidgetCMdIHf.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)

class Ui_ThumbnailWidget(object):
    def setupUi(self, ThumbnailWidget):
        if not ThumbnailWidget.objectName():
            ThumbnailWidget.setObjectName(u"ThumbnailWidget")
        ThumbnailWidget.resize(310, 90)
        ThumbnailWidget.setMinimumSize(QSize(310, 90))
        ThumbnailWidget.setBaseSize(QSize(310, 90))
        self.horizontalLayout = QHBoxLayout(ThumbnailWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.thumbnail_h_layout = QHBoxLayout()
        self.thumbnail_h_layout.setObjectName(u"thumbnail_h_layout")
        self.thumbnail_image = QLabel(ThumbnailWidget)
        self.thumbnail_image.setObjectName(u"thumbnail_image")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.thumbnail_image.sizePolicy().hasHeightForWidth())
        self.thumbnail_image.setSizePolicy(sizePolicy)
        self.thumbnail_image.setMinimumSize(QSize(128, 64))
        self.thumbnail_image.setMaximumSize(QSize(128, 64))
        self.thumbnail_image.setBaseSize(QSize(128, 64))

        self.thumbnail_h_layout.addWidget(self.thumbnail_image)

        self.thumbnail_v_layout = QVBoxLayout()
        self.thumbnail_v_layout.setObjectName(u"thumbnail_v_layout")
        self.song_id_lineedit = QLineEdit(ThumbnailWidget)
        self.song_id_lineedit.setObjectName(u"song_id_lineedit")
        self.song_id_lineedit.setFrame(True)
        self.song_id_lineedit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.song_id_lineedit.setClearButtonEnabled(False)

        self.thumbnail_v_layout.addWidget(self.song_id_lineedit)

        self.remove_thumbnail_button = QPushButton(ThumbnailWidget)
        self.remove_thumbnail_button.setObjectName(u"remove_thumbnail_button")

        self.thumbnail_v_layout.addWidget(self.remove_thumbnail_button)


        self.thumbnail_h_layout.addLayout(self.thumbnail_v_layout)


        self.horizontalLayout.addLayout(self.thumbnail_h_layout)


        self.retranslateUi(ThumbnailWidget)

        QMetaObject.connectSlotsByName(ThumbnailWidget)
    # setupUi

    def retranslateUi(self, ThumbnailWidget):
        ThumbnailWidget.setWindowTitle(QCoreApplication.translate("ThumbnailWidget", u"Thumbnail Widget", None))
        self.thumbnail_image.setText("")
        self.song_id_lineedit.setInputMask(QCoreApplication.translate("ThumbnailWidget", u"0000000000", None))
        self.song_id_lineedit.setText("")
        self.song_id_lineedit.setPlaceholderText(QCoreApplication.translate("ThumbnailWidget", u"Enter Song ID here", None))
        self.remove_thumbnail_button.setText(QCoreApplication.translate("ThumbnailWidget", u"Remove Thumbnail", None))
    # retranslateUi

