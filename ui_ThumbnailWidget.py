# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ThumbnailWidgetdmlYwO.ui'
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QHBoxLayout, QLabel,
    QLayout, QLineEdit, QPushButton, QScrollArea,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_ThumbnailWidget(object):
    def setupUi(self, ThumbnailWidget):
        if not ThumbnailWidget.objectName():
            ThumbnailWidget.setObjectName(u"ThumbnailWidget")
        ThumbnailWidget.setEnabled(True)
        ThumbnailWidget.resize(365, 150)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ThumbnailWidget.sizePolicy().hasHeightForWidth())
        ThumbnailWidget.setSizePolicy(sizePolicy)
        ThumbnailWidget.setMinimumSize(QSize(365, 95))
        ThumbnailWidget.setMaximumSize(QSize(365, 150))
        ThumbnailWidget.setBaseSize(QSize(310, 90))
        self.horizontalLayout = QHBoxLayout(ThumbnailWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.thumbnail_h_layout = QHBoxLayout()
        self.thumbnail_h_layout.setObjectName(u"thumbnail_h_layout")
        self.thumbnail_image = QLabel(ThumbnailWidget)
        self.thumbnail_image.setObjectName(u"thumbnail_image")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.thumbnail_image.sizePolicy().hasHeightForWidth())
        self.thumbnail_image.setSizePolicy(sizePolicy1)
        self.thumbnail_image.setMinimumSize(QSize(128, 64))
        self.thumbnail_image.setMaximumSize(QSize(128, 64))
        self.thumbnail_image.setBaseSize(QSize(128, 64))

        self.thumbnail_h_layout.addWidget(self.thumbnail_image)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.scrollArea = QScrollArea(ThumbnailWidget)
        self.scrollArea.setObjectName(u"scrollArea")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy2)
        self.scrollArea.setMinimumSize(QSize(208, 37))
        self.scrollArea.setMaximumSize(QSize(208, 95))
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 206, 91))
        self.formLayout = QFormLayout(self.scrollAreaWidgetContents)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.formLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.formLayout.setHorizontalSpacing(0)
        self.formLayout.setVerticalSpacing(0)
        self.formLayout.setContentsMargins(0, 4, 0, 0)
        self.song_id_lineedit = QLineEdit(self.scrollAreaWidgetContents)
        self.song_id_lineedit.setObjectName(u"song_id_lineedit")
        sizePolicy1.setHeightForWidth(self.song_id_lineedit.sizePolicy().hasHeightForWidth())
        self.song_id_lineedit.setSizePolicy(sizePolicy1)
        self.song_id_lineedit.setMinimumSize(QSize(154, 27))
        self.song_id_lineedit.setMaximumSize(QSize(154, 27))
        self.song_id_lineedit.setFrame(True)
        self.song_id_lineedit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.song_id_lineedit.setClearButtonEnabled(False)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.song_id_lineedit)

        self.add_additional_id_line_button = QPushButton(self.scrollAreaWidgetContents)
        self.add_additional_id_line_button.setObjectName(u"add_additional_id_line_button")
        self.add_additional_id_line_button.setMinimumSize(QSize(30, 27))
        self.add_additional_id_line_button.setMaximumSize(QSize(30, 27))
        palette = QPalette()
        brush = QBrush(QColor(87, 227, 137, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, brush)
        self.add_additional_id_line_button.setPalette(palette)
        font = QFont()
        font.setPointSize(11)
        self.add_additional_id_line_button.setFont(font)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.add_additional_id_line_button)

        self.song_id_lineedit_1 = QLineEdit(self.scrollAreaWidgetContents)
        self.song_id_lineedit_1.setObjectName(u"song_id_lineedit_1")
        sizePolicy1.setHeightForWidth(self.song_id_lineedit_1.sizePolicy().hasHeightForWidth())
        self.song_id_lineedit_1.setSizePolicy(sizePolicy1)
        self.song_id_lineedit_1.setMinimumSize(QSize(154, 27))
        self.song_id_lineedit_1.setMaximumSize(QSize(154, 27))
        self.song_id_lineedit_1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.song_id_lineedit_1)

        self.remove_additional_id_line_button = QPushButton(self.scrollAreaWidgetContents)
        self.remove_additional_id_line_button.setObjectName(u"remove_additional_id_line_button")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.remove_additional_id_line_button.sizePolicy().hasHeightForWidth())
        self.remove_additional_id_line_button.setSizePolicy(sizePolicy3)
        self.remove_additional_id_line_button.setMinimumSize(QSize(30, 27))
        self.remove_additional_id_line_button.setMaximumSize(QSize(30, 27))
        palette1 = QPalette()
        brush1 = QBrush(QColor(191, 64, 64, 255))
        brush1.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, brush1)
        brush2 = QBrush(QColor(237, 51, 59, 255))
        brush2.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush2)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, brush1)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, brush2)
        self.remove_additional_id_line_button.setPalette(palette1)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.remove_additional_id_line_button)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)

        self.thumbnail_v_layout = QVBoxLayout()
        self.thumbnail_v_layout.setObjectName(u"thumbnail_v_layout")
        self.remove_thumbnail_button = QPushButton(ThumbnailWidget)
        self.remove_thumbnail_button.setObjectName(u"remove_thumbnail_button")
        sizePolicy1.setHeightForWidth(self.remove_thumbnail_button.sizePolicy().hasHeightForWidth())
        self.remove_thumbnail_button.setSizePolicy(sizePolicy1)
        self.remove_thumbnail_button.setMinimumSize(QSize(206, 27))
        self.remove_thumbnail_button.setMaximumSize(QSize(206, 27))

        self.thumbnail_v_layout.addWidget(self.remove_thumbnail_button)


        self.verticalLayout.addLayout(self.thumbnail_v_layout)


        self.thumbnail_h_layout.addLayout(self.verticalLayout)


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
        self.add_additional_id_line_button.setText(QCoreApplication.translate("ThumbnailWidget", u"+", None))
        self.song_id_lineedit_1.setInputMask(QCoreApplication.translate("ThumbnailWidget", u"0000000000", None))
        self.song_id_lineedit_1.setText("")
        self.song_id_lineedit_1.setPlaceholderText(QCoreApplication.translate("ThumbnailWidget", u"Enter Song ID here", None))
        self.remove_additional_id_line_button.setText(QCoreApplication.translate("ThumbnailWidget", u"-", None))
        self.remove_thumbnail_button.setText(QCoreApplication.translate("ThumbnailWidget", u"Remove Thumbnail", None))
    # retranslateUi

