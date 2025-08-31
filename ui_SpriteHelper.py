# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SpriteHelper_noFarcXGDGgC.ui'
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
from PySide6.QtWidgets import (QAbstractScrollArea, QAbstractSpinBox, QApplication, QCheckBox,
    QDoubleSpinBox, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QLayout, QMainWindow, QPushButton,
    QScrollArea, QSizePolicy, QSpacerItem, QSpinBox,
    QVBoxLayout, QWidget)

from widgets import QLabel_clickable

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setWindowModality(Qt.WindowModality.NonModal)
        MainWindow.resize(1200, 600)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(1200, 600))
        MainWindow.setSizeIncrement(QSize(0, 0))
        MainWindow.setBaseSize(QSize(1200, 600))
        font = QFont()
        font.setFamilies([u"Nimbus Sans Narrow [UKWN]"])
        font.setPointSize(11)
        font.setBold(False)
        font.setKerning(True)
        MainWindow.setFont(font)
        MainWindow.setAcceptDrops(False)
        MainWindow.setWindowTitle(u"Megamix Sprite Helper")
        icon = QIcon()
        icon.addFile(u":/icon/Icon.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setAutoFillBackground(True)
        MainWindow.setLocale(QLocale(QLocale.English, QLocale.Europe))
        MainWindow.setAnimated(True)
        MainWindow.setDocumentMode(False)
        self.grid = QWidget(MainWindow)
        self.grid.setObjectName(u"grid")
        self.grid.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.grid.sizePolicy().hasHeightForWidth())
        self.grid.setSizePolicy(sizePolicy1)
        self.grid.setMinimumSize(QSize(0, 0))
        self.grid.setSizeIncrement(QSize(0, 0))
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
        self.ft_song_selector_preview = QLabel_clickable(self.grid)
        self.ft_song_selector_preview.setObjectName(u"ft_song_selector_preview")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        sizePolicy2.setHorizontalStretch(1)
        sizePolicy2.setVerticalStretch(1)
        sizePolicy2.setHeightForWidth(self.ft_song_selector_preview.sizePolicy().hasHeightForWidth())
        self.ft_song_selector_preview.setSizePolicy(sizePolicy2)
        self.ft_song_selector_preview.setMinimumSize(QSize(256, 144))
        self.ft_song_selector_preview.setMaximumSize(QSize(1920, 1080))
        self.ft_song_selector_preview.setSizeIncrement(QSize(0, 0))
        self.ft_song_selector_preview.setBaseSize(QSize(640, 360))
        self.ft_song_selector_preview.setScaledContents(True)

        self.image_grid.addWidget(self.ft_song_selector_preview, 0, 1, 1, 1)

        self.mm_result_preview = QLabel_clickable(self.grid)
        self.mm_result_preview.setObjectName(u"mm_result_preview")
        sizePolicy2.setHeightForWidth(self.mm_result_preview.sizePolicy().hasHeightForWidth())
        self.mm_result_preview.setSizePolicy(sizePolicy2)
        self.mm_result_preview.setMinimumSize(QSize(256, 144))
        self.mm_result_preview.setMaximumSize(QSize(1920, 1080))
        self.mm_result_preview.setSizeIncrement(QSize(0, 0))
        self.mm_result_preview.setBaseSize(QSize(640, 360))
        self.mm_result_preview.setScaledContents(True)

        self.image_grid.addWidget(self.mm_result_preview, 1, 0, 1, 1)

        self.mm_song_selector_preview = QLabel_clickable(self.grid)
        self.mm_song_selector_preview.setObjectName(u"mm_song_selector_preview")
        sizePolicy2.setHeightForWidth(self.mm_song_selector_preview.sizePolicy().hasHeightForWidth())
        self.mm_song_selector_preview.setSizePolicy(sizePolicy2)
        self.mm_song_selector_preview.setMinimumSize(QSize(256, 144))
        self.mm_song_selector_preview.setMaximumSize(QSize(1920, 1080))
        self.mm_song_selector_preview.setSizeIncrement(QSize(0, 0))
        self.mm_song_selector_preview.setBaseSize(QSize(640, 360))
        self.mm_song_selector_preview.setScaledContents(True)

        self.image_grid.addWidget(self.mm_song_selector_preview, 0, 0, 1, 1)

        self.ft_result_preview = QLabel_clickable(self.grid)
        self.ft_result_preview.setObjectName(u"ft_result_preview")
        sizePolicy2.setHeightForWidth(self.ft_result_preview.sizePolicy().hasHeightForWidth())
        self.ft_result_preview.setSizePolicy(sizePolicy2)
        self.ft_result_preview.setMinimumSize(QSize(256, 144))
        self.ft_result_preview.setMaximumSize(QSize(1920, 1080))
        self.ft_result_preview.setSizeIncrement(QSize(0, 0))
        self.ft_result_preview.setBaseSize(QSize(640, 360))
        self.ft_result_preview.setScaledContents(True)

        self.image_grid.addWidget(self.ft_result_preview, 1, 1, 1, 1)


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
        self.load_buttons_box_row3.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.load_buttons_box_row3.setContentsMargins(-1, 0, -1, -1)
        self.has_logo_checkbox = QCheckBox(self.grid)
        self.has_logo_checkbox.setObjectName(u"has_logo_checkbox")
        self.has_logo_checkbox.setCheckable(True)
        self.has_logo_checkbox.setChecked(True)

        self.load_buttons_box_row3.addWidget(self.has_logo_checkbox)

        self.new_classics_checkbox = QCheckBox(self.grid)
        self.new_classics_checkbox.setObjectName(u"new_classics_checkbox")
        self.new_classics_checkbox.setChecked(True)

        self.load_buttons_box_row3.addWidget(self.new_classics_checkbox)


        self.load_buttons_box.addLayout(self.load_buttons_box_row3)

        self.image_edit_scroll_area = QScrollArea(self.grid)
        self.image_edit_scroll_area.setObjectName(u"image_edit_scroll_area")
        self.image_edit_scroll_area.setEnabled(True)
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.image_edit_scroll_area.sizePolicy().hasHeightForWidth())
        self.image_edit_scroll_area.setSizePolicy(sizePolicy3)
        self.image_edit_scroll_area.setAutoFillBackground(False)
        self.image_edit_scroll_area.setFrameShape(QFrame.Shape.StyledPanel)
        self.image_edit_scroll_area.setFrameShadow(QFrame.Shadow.Sunken)
        self.image_edit_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.image_edit_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.image_edit_scroll_area.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.image_edit_scroll_area.setWidgetResizable(True)
        self.image_edit_scroll_area.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft)
        self.image_edit_area_widget_properties = QWidget()
        self.image_edit_area_widget_properties.setObjectName(u"image_edit_area_widget_properties")
        self.image_edit_area_widget_properties.setGeometry(QRect(0, 0, 181, 905))
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.image_edit_area_widget_properties.sizePolicy().hasHeightForWidth())
        self.image_edit_area_widget_properties.setSizePolicy(sizePolicy4)
        self.image_edit_area_widget_properties.setMinimumSize(QSize(0, 905))
        self.image_edit_area_widget_properties.setMaximumSize(QSize(16777215, 16777215))
        self.image_edit_area_widget_properties.setSizeIncrement(QSize(0, -31072))
        self.image_edit_area_widget_properties.setBaseSize(QSize(0, -31072))
        self.image_edit_area_widget_properties.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
        self.image_edit_area_widget_properties.setAutoFillBackground(True)
        self.verticalLayoutWidget_3 = QWidget(self.image_edit_area_widget_properties)
        self.verticalLayoutWidget_3.setObjectName(u"verticalLayoutWidget_3")
        self.verticalLayoutWidget_3.setGeometry(QRect(0, 0, 329, 2082))
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget_3)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.jacket_horizontal_offset_label = QLabel(self.verticalLayoutWidget_3)
        self.jacket_horizontal_offset_label.setObjectName(u"jacket_horizontal_offset_label")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.jacket_horizontal_offset_label.sizePolicy().hasHeightForWidth())
        self.jacket_horizontal_offset_label.setSizePolicy(sizePolicy5)
        self.jacket_horizontal_offset_label.setMaximumSize(QSize(16777215, 16777215))
        font1 = QFont()
        font1.setFamilies([u"Nimbus Sans Narrow [UKWN]"])
        font1.setPointSize(9)
        font1.setBold(False)
        font1.setKerning(True)
        self.jacket_horizontal_offset_label.setFont(font1)

        self.verticalLayout_2.addWidget(self.jacket_horizontal_offset_label)

        self.jacket_horizontal_offset_spinbox = QSpinBox(self.verticalLayoutWidget_3)
        self.jacket_horizontal_offset_spinbox.setObjectName(u"jacket_horizontal_offset_spinbox")
        self.jacket_horizontal_offset_spinbox.setEnabled(False)
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.jacket_horizontal_offset_spinbox.sizePolicy().hasHeightForWidth())
        self.jacket_horizontal_offset_spinbox.setSizePolicy(sizePolicy6)
        self.jacket_horizontal_offset_spinbox.setMaximumSize(QSize(160, 16777215))
        self.jacket_horizontal_offset_spinbox.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.jacket_horizontal_offset_spinbox.setMinimum(0)
        self.jacket_horizontal_offset_spinbox.setMaximum(0)

        self.verticalLayout_2.addWidget(self.jacket_horizontal_offset_spinbox)

        self.jacket_vertical_offset_label = QLabel(self.verticalLayoutWidget_3)
        self.jacket_vertical_offset_label.setObjectName(u"jacket_vertical_offset_label")
        sizePolicy5.setHeightForWidth(self.jacket_vertical_offset_label.sizePolicy().hasHeightForWidth())
        self.jacket_vertical_offset_label.setSizePolicy(sizePolicy5)
        self.jacket_vertical_offset_label.setMaximumSize(QSize(16777215, 16777215))
        self.jacket_vertical_offset_label.setFont(font1)

        self.verticalLayout_2.addWidget(self.jacket_vertical_offset_label)

        self.jacket_vertical_offset_spinbox = QSpinBox(self.verticalLayoutWidget_3)
        self.jacket_vertical_offset_spinbox.setObjectName(u"jacket_vertical_offset_spinbox")
        self.jacket_vertical_offset_spinbox.setEnabled(False)
        sizePolicy6.setHeightForWidth(self.jacket_vertical_offset_spinbox.sizePolicy().hasHeightForWidth())
        self.jacket_vertical_offset_spinbox.setSizePolicy(sizePolicy6)
        self.jacket_vertical_offset_spinbox.setMaximumSize(QSize(160, 16777215))
        self.jacket_vertical_offset_spinbox.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.jacket_vertical_offset_spinbox.setMinimum(0)
        self.jacket_vertical_offset_spinbox.setMaximum(0)

        self.verticalLayout_2.addWidget(self.jacket_vertical_offset_spinbox)

        self.jacket_rotation_label = QLabel(self.verticalLayoutWidget_3)
        self.jacket_rotation_label.setObjectName(u"jacket_rotation_label")
        sizePolicy5.setHeightForWidth(self.jacket_rotation_label.sizePolicy().hasHeightForWidth())
        self.jacket_rotation_label.setSizePolicy(sizePolicy5)
        self.jacket_rotation_label.setMaximumSize(QSize(16777215, 16777215))
        self.jacket_rotation_label.setFont(font1)

        self.verticalLayout_2.addWidget(self.jacket_rotation_label)

        self.jacket_rotation_spinbox = QSpinBox(self.verticalLayoutWidget_3)
        self.jacket_rotation_spinbox.setObjectName(u"jacket_rotation_spinbox")
        sizePolicy6.setHeightForWidth(self.jacket_rotation_spinbox.sizePolicy().hasHeightForWidth())
        self.jacket_rotation_spinbox.setSizePolicy(sizePolicy6)
        self.jacket_rotation_spinbox.setMaximumSize(QSize(160, 16777215))
        self.jacket_rotation_spinbox.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.jacket_rotation_spinbox.setWrapping(True)
        self.jacket_rotation_spinbox.setCorrectionMode(QAbstractSpinBox.CorrectionMode.CorrectToNearestValue)
        self.jacket_rotation_spinbox.setMinimum(-180)
        self.jacket_rotation_spinbox.setMaximum(180)

        self.verticalLayout_2.addWidget(self.jacket_rotation_spinbox)

        self.jacket_zoom_label = QLabel(self.verticalLayoutWidget_3)
        self.jacket_zoom_label.setObjectName(u"jacket_zoom_label")
        sizePolicy5.setHeightForWidth(self.jacket_zoom_label.sizePolicy().hasHeightForWidth())
        self.jacket_zoom_label.setSizePolicy(sizePolicy5)
        self.jacket_zoom_label.setMaximumSize(QSize(16777215, 16777215))
        self.jacket_zoom_label.setFont(font1)

        self.verticalLayout_2.addWidget(self.jacket_zoom_label)

        self.jacket_zoom_spinbox = QDoubleSpinBox(self.verticalLayoutWidget_3)
        self.jacket_zoom_spinbox.setObjectName(u"jacket_zoom_spinbox")
        self.jacket_zoom_spinbox.setEnabled(False)
        sizePolicy6.setHeightForWidth(self.jacket_zoom_spinbox.sizePolicy().hasHeightForWidth())
        self.jacket_zoom_spinbox.setSizePolicy(sizePolicy6)
        self.jacket_zoom_spinbox.setMaximumSize(QSize(160, 16777215))
        self.jacket_zoom_spinbox.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.jacket_zoom_spinbox.setAccelerated(True)
        self.jacket_zoom_spinbox.setDecimals(3)
        self.jacket_zoom_spinbox.setMinimum(1.000000000000000)
        self.jacket_zoom_spinbox.setMaximum(1.000000000000000)
        self.jacket_zoom_spinbox.setSingleStep(0.001000000000000)
        self.jacket_zoom_spinbox.setValue(1.000000000000000)

        self.verticalLayout_2.addWidget(self.jacket_zoom_spinbox)

        self.background_horizontal_offset_label = QLabel(self.verticalLayoutWidget_3)
        self.background_horizontal_offset_label.setObjectName(u"background_horizontal_offset_label")
        sizePolicy5.setHeightForWidth(self.background_horizontal_offset_label.sizePolicy().hasHeightForWidth())
        self.background_horizontal_offset_label.setSizePolicy(sizePolicy5)
        self.background_horizontal_offset_label.setMaximumSize(QSize(16777215, 16777215))
        self.background_horizontal_offset_label.setFont(font1)

        self.verticalLayout_2.addWidget(self.background_horizontal_offset_label)

        self.background_horizontal_offset_spinbox = QSpinBox(self.verticalLayoutWidget_3)
        self.background_horizontal_offset_spinbox.setObjectName(u"background_horizontal_offset_spinbox")
        self.background_horizontal_offset_spinbox.setEnabled(False)
        sizePolicy6.setHeightForWidth(self.background_horizontal_offset_spinbox.sizePolicy().hasHeightForWidth())
        self.background_horizontal_offset_spinbox.setSizePolicy(sizePolicy6)
        self.background_horizontal_offset_spinbox.setMaximumSize(QSize(160, 16777215))
        self.background_horizontal_offset_spinbox.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.background_horizontal_offset_spinbox.setWrapping(False)
        self.background_horizontal_offset_spinbox.setMaximum(0)

        self.verticalLayout_2.addWidget(self.background_horizontal_offset_spinbox)

        self.background_vertical_offset_label = QLabel(self.verticalLayoutWidget_3)
        self.background_vertical_offset_label.setObjectName(u"background_vertical_offset_label")
        sizePolicy5.setHeightForWidth(self.background_vertical_offset_label.sizePolicy().hasHeightForWidth())
        self.background_vertical_offset_label.setSizePolicy(sizePolicy5)
        self.background_vertical_offset_label.setMaximumSize(QSize(16777215, 16777215))
        self.background_vertical_offset_label.setFont(font1)

        self.verticalLayout_2.addWidget(self.background_vertical_offset_label)

        self.background_vertical_offset_spinbox = QSpinBox(self.verticalLayoutWidget_3)
        self.background_vertical_offset_spinbox.setObjectName(u"background_vertical_offset_spinbox")
        self.background_vertical_offset_spinbox.setEnabled(False)
        sizePolicy6.setHeightForWidth(self.background_vertical_offset_spinbox.sizePolicy().hasHeightForWidth())
        self.background_vertical_offset_spinbox.setSizePolicy(sizePolicy6)
        self.background_vertical_offset_spinbox.setMaximumSize(QSize(160, 16777215))
        self.background_vertical_offset_spinbox.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.background_vertical_offset_spinbox.setMaximum(0)

        self.verticalLayout_2.addWidget(self.background_vertical_offset_spinbox)

        self.background_rotation_label = QLabel(self.verticalLayoutWidget_3)
        self.background_rotation_label.setObjectName(u"background_rotation_label")
        sizePolicy5.setHeightForWidth(self.background_rotation_label.sizePolicy().hasHeightForWidth())
        self.background_rotation_label.setSizePolicy(sizePolicy5)
        self.background_rotation_label.setMaximumSize(QSize(16777215, 16777215))
        self.background_rotation_label.setFont(font1)

        self.verticalLayout_2.addWidget(self.background_rotation_label)

        self.background_rotation_spinbox = QSpinBox(self.verticalLayoutWidget_3)
        self.background_rotation_spinbox.setObjectName(u"background_rotation_spinbox")
        sizePolicy6.setHeightForWidth(self.background_rotation_spinbox.sizePolicy().hasHeightForWidth())
        self.background_rotation_spinbox.setSizePolicy(sizePolicy6)
        self.background_rotation_spinbox.setMaximumSize(QSize(160, 16777215))
        self.background_rotation_spinbox.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.background_rotation_spinbox.setWrapping(True)
        self.background_rotation_spinbox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.background_rotation_spinbox.setCorrectionMode(QAbstractSpinBox.CorrectionMode.CorrectToNearestValue)
        self.background_rotation_spinbox.setProperty(u"showGroupSeparator", False)
        self.background_rotation_spinbox.setMinimum(-180)
        self.background_rotation_spinbox.setMaximum(180)

        self.verticalLayout_2.addWidget(self.background_rotation_spinbox)

        self.background_zoom_label = QLabel(self.verticalLayoutWidget_3)
        self.background_zoom_label.setObjectName(u"background_zoom_label")
        sizePolicy5.setHeightForWidth(self.background_zoom_label.sizePolicy().hasHeightForWidth())
        self.background_zoom_label.setSizePolicy(sizePolicy5)
        self.background_zoom_label.setMaximumSize(QSize(16777215, 16777215))
        self.background_zoom_label.setFont(font1)

        self.verticalLayout_2.addWidget(self.background_zoom_label)

        self.background_zoom_spinbox = QDoubleSpinBox(self.verticalLayoutWidget_3)
        self.background_zoom_spinbox.setObjectName(u"background_zoom_spinbox")
        self.background_zoom_spinbox.setEnabled(False)
        sizePolicy6.setHeightForWidth(self.background_zoom_spinbox.sizePolicy().hasHeightForWidth())
        self.background_zoom_spinbox.setSizePolicy(sizePolicy6)
        self.background_zoom_spinbox.setMaximumSize(QSize(160, 16777215))
        self.background_zoom_spinbox.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.background_zoom_spinbox.setAccelerated(True)
        self.background_zoom_spinbox.setDecimals(3)
        self.background_zoom_spinbox.setMinimum(1.000000000000000)
        self.background_zoom_spinbox.setMaximum(1.000000000000000)
        self.background_zoom_spinbox.setSingleStep(0.001000000000000)
        self.background_zoom_spinbox.setValue(1.000000000000000)

        self.verticalLayout_2.addWidget(self.background_zoom_spinbox)

        self.logo_horizontal_offset_label = QLabel(self.verticalLayoutWidget_3)
        self.logo_horizontal_offset_label.setObjectName(u"logo_horizontal_offset_label")
        self.logo_horizontal_offset_label.setEnabled(True)
        sizePolicy5.setHeightForWidth(self.logo_horizontal_offset_label.sizePolicy().hasHeightForWidth())
        self.logo_horizontal_offset_label.setSizePolicy(sizePolicy5)
        self.logo_horizontal_offset_label.setMaximumSize(QSize(16777215, 16777215))
        self.logo_horizontal_offset_label.setFont(font1)

        self.verticalLayout_2.addWidget(self.logo_horizontal_offset_label)

        self.logo_horizontal_offset_spinbox = QSpinBox(self.verticalLayoutWidget_3)
        self.logo_horizontal_offset_spinbox.setObjectName(u"logo_horizontal_offset_spinbox")
        self.logo_horizontal_offset_spinbox.setEnabled(True)
        sizePolicy6.setHeightForWidth(self.logo_horizontal_offset_spinbox.sizePolicy().hasHeightForWidth())
        self.logo_horizontal_offset_spinbox.setSizePolicy(sizePolicy6)
        self.logo_horizontal_offset_spinbox.setMaximumSize(QSize(160, 16777215))
        self.logo_horizontal_offset_spinbox.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.logo_horizontal_offset_spinbox.setMinimum(-435)
        self.logo_horizontal_offset_spinbox.setMaximum(435)

        self.verticalLayout_2.addWidget(self.logo_horizontal_offset_spinbox)

        self.logo_vertical_offset_label = QLabel(self.verticalLayoutWidget_3)
        self.logo_vertical_offset_label.setObjectName(u"logo_vertical_offset_label")
        self.logo_vertical_offset_label.setEnabled(True)
        sizePolicy5.setHeightForWidth(self.logo_vertical_offset_label.sizePolicy().hasHeightForWidth())
        self.logo_vertical_offset_label.setSizePolicy(sizePolicy5)
        self.logo_vertical_offset_label.setMaximumSize(QSize(16777215, 16777215))
        self.logo_vertical_offset_label.setFont(font1)

        self.verticalLayout_2.addWidget(self.logo_vertical_offset_label)

        self.logo_vertical_offset_spinbox = QSpinBox(self.verticalLayoutWidget_3)
        self.logo_vertical_offset_spinbox.setObjectName(u"logo_vertical_offset_spinbox")
        self.logo_vertical_offset_spinbox.setEnabled(True)
        sizePolicy6.setHeightForWidth(self.logo_vertical_offset_spinbox.sizePolicy().hasHeightForWidth())
        self.logo_vertical_offset_spinbox.setSizePolicy(sizePolicy6)
        self.logo_vertical_offset_spinbox.setMaximumSize(QSize(160, 16777215))
        self.logo_vertical_offset_spinbox.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.logo_vertical_offset_spinbox.setMinimum(-150)
        self.logo_vertical_offset_spinbox.setMaximum(150)

        self.verticalLayout_2.addWidget(self.logo_vertical_offset_spinbox)

        self.logo_rotation_label = QLabel(self.verticalLayoutWidget_3)
        self.logo_rotation_label.setObjectName(u"logo_rotation_label")
        self.logo_rotation_label.setEnabled(True)
        sizePolicy5.setHeightForWidth(self.logo_rotation_label.sizePolicy().hasHeightForWidth())
        self.logo_rotation_label.setSizePolicy(sizePolicy5)
        self.logo_rotation_label.setMaximumSize(QSize(16777215, 16777215))
        self.logo_rotation_label.setFont(font1)

        self.verticalLayout_2.addWidget(self.logo_rotation_label)

        self.logo_rotation_spinbox = QSpinBox(self.verticalLayoutWidget_3)
        self.logo_rotation_spinbox.setObjectName(u"logo_rotation_spinbox")
        self.logo_rotation_spinbox.setEnabled(True)
        sizePolicy6.setHeightForWidth(self.logo_rotation_spinbox.sizePolicy().hasHeightForWidth())
        self.logo_rotation_spinbox.setSizePolicy(sizePolicy6)
        self.logo_rotation_spinbox.setMaximumSize(QSize(160, 16777215))
        self.logo_rotation_spinbox.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.logo_rotation_spinbox.setWrapping(True)
        self.logo_rotation_spinbox.setCorrectionMode(QAbstractSpinBox.CorrectionMode.CorrectToNearestValue)
        self.logo_rotation_spinbox.setMinimum(-180)
        self.logo_rotation_spinbox.setValue(0)

        self.verticalLayout_2.addWidget(self.logo_rotation_spinbox)

        self.logo_zoom_label = QLabel(self.verticalLayoutWidget_3)
        self.logo_zoom_label.setObjectName(u"logo_zoom_label")
        self.logo_zoom_label.setEnabled(True)
        sizePolicy5.setHeightForWidth(self.logo_zoom_label.sizePolicy().hasHeightForWidth())
        self.logo_zoom_label.setSizePolicy(sizePolicy5)
        self.logo_zoom_label.setMaximumSize(QSize(16777215, 16777215))
        self.logo_zoom_label.setFont(font1)

        self.verticalLayout_2.addWidget(self.logo_zoom_label)

        self.logo_zoom_spinbox = QDoubleSpinBox(self.verticalLayoutWidget_3)
        self.logo_zoom_spinbox.setObjectName(u"logo_zoom_spinbox")
        self.logo_zoom_spinbox.setEnabled(True)
        sizePolicy6.setHeightForWidth(self.logo_zoom_spinbox.sizePolicy().hasHeightForWidth())
        self.logo_zoom_spinbox.setSizePolicy(sizePolicy6)
        self.logo_zoom_spinbox.setMaximumSize(QSize(160, 16777215))
        self.logo_zoom_spinbox.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.logo_zoom_spinbox.setAccelerated(True)
        self.logo_zoom_spinbox.setDecimals(3)
        self.logo_zoom_spinbox.setMinimum(0.001000000000000)
        self.logo_zoom_spinbox.setMaximum(1.000000000000000)
        self.logo_zoom_spinbox.setSingleStep(0.001000000000000)
        self.logo_zoom_spinbox.setValue(1.000000000000000)

        self.verticalLayout_2.addWidget(self.logo_zoom_spinbox)

        self.thumbnail_horizontal_offset_label = QLabel(self.verticalLayoutWidget_3)
        self.thumbnail_horizontal_offset_label.setObjectName(u"thumbnail_horizontal_offset_label")
        sizePolicy5.setHeightForWidth(self.thumbnail_horizontal_offset_label.sizePolicy().hasHeightForWidth())
        self.thumbnail_horizontal_offset_label.setSizePolicy(sizePolicy5)
        self.thumbnail_horizontal_offset_label.setMaximumSize(QSize(16777215, 16777215))
        self.thumbnail_horizontal_offset_label.setFont(font1)

        self.verticalLayout_2.addWidget(self.thumbnail_horizontal_offset_label)

        self.thumbnail_horizontal_offset_spinbox = QSpinBox(self.verticalLayoutWidget_3)
        self.thumbnail_horizontal_offset_spinbox.setObjectName(u"thumbnail_horizontal_offset_spinbox")
        sizePolicy6.setHeightForWidth(self.thumbnail_horizontal_offset_spinbox.sizePolicy().hasHeightForWidth())
        self.thumbnail_horizontal_offset_spinbox.setSizePolicy(sizePolicy6)
        self.thumbnail_horizontal_offset_spinbox.setMaximumSize(QSize(160, 16777215))
        self.thumbnail_horizontal_offset_spinbox.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.thumbnail_horizontal_offset_spinbox.setMaximum(27)

        self.verticalLayout_2.addWidget(self.thumbnail_horizontal_offset_spinbox)

        self.thumbnail_vertical_offset_label = QLabel(self.verticalLayoutWidget_3)
        self.thumbnail_vertical_offset_label.setObjectName(u"thumbnail_vertical_offset_label")
        sizePolicy5.setHeightForWidth(self.thumbnail_vertical_offset_label.sizePolicy().hasHeightForWidth())
        self.thumbnail_vertical_offset_label.setSizePolicy(sizePolicy5)
        self.thumbnail_vertical_offset_label.setMaximumSize(QSize(16777215, 16777215))
        self.thumbnail_vertical_offset_label.setFont(font1)

        self.verticalLayout_2.addWidget(self.thumbnail_vertical_offset_label)

        self.thumbnail_vertical_offset_spinbox = QSpinBox(self.verticalLayoutWidget_3)
        self.thumbnail_vertical_offset_spinbox.setObjectName(u"thumbnail_vertical_offset_spinbox")
        self.thumbnail_vertical_offset_spinbox.setEnabled(False)
        sizePolicy6.setHeightForWidth(self.thumbnail_vertical_offset_spinbox.sizePolicy().hasHeightForWidth())
        self.thumbnail_vertical_offset_spinbox.setSizePolicy(sizePolicy6)
        self.thumbnail_vertical_offset_spinbox.setMaximumSize(QSize(160, 16777215))
        self.thumbnail_vertical_offset_spinbox.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.thumbnail_vertical_offset_spinbox.setMaximum(0)

        self.verticalLayout_2.addWidget(self.thumbnail_vertical_offset_spinbox)

        self.thumbnail_rotation_label = QLabel(self.verticalLayoutWidget_3)
        self.thumbnail_rotation_label.setObjectName(u"thumbnail_rotation_label")
        sizePolicy5.setHeightForWidth(self.thumbnail_rotation_label.sizePolicy().hasHeightForWidth())
        self.thumbnail_rotation_label.setSizePolicy(sizePolicy5)
        self.thumbnail_rotation_label.setMaximumSize(QSize(16777215, 16777215))
        self.thumbnail_rotation_label.setFont(font1)

        self.verticalLayout_2.addWidget(self.thumbnail_rotation_label)

        self.thumbnail_rotation_spinbox = QSpinBox(self.verticalLayoutWidget_3)
        self.thumbnail_rotation_spinbox.setObjectName(u"thumbnail_rotation_spinbox")
        sizePolicy6.setHeightForWidth(self.thumbnail_rotation_spinbox.sizePolicy().hasHeightForWidth())
        self.thumbnail_rotation_spinbox.setSizePolicy(sizePolicy6)
        self.thumbnail_rotation_spinbox.setMaximumSize(QSize(160, 16777215))
        self.thumbnail_rotation_spinbox.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.thumbnail_rotation_spinbox.setWrapping(True)
        self.thumbnail_rotation_spinbox.setCorrectionMode(QAbstractSpinBox.CorrectionMode.CorrectToNearestValue)
        self.thumbnail_rotation_spinbox.setMinimum(-180)
        self.thumbnail_rotation_spinbox.setMaximum(180)

        self.verticalLayout_2.addWidget(self.thumbnail_rotation_spinbox)

        self.thumbnail_zoom_label = QLabel(self.verticalLayoutWidget_3)
        self.thumbnail_zoom_label.setObjectName(u"thumbnail_zoom_label")
        sizePolicy5.setHeightForWidth(self.thumbnail_zoom_label.sizePolicy().hasHeightForWidth())
        self.thumbnail_zoom_label.setSizePolicy(sizePolicy5)
        self.thumbnail_zoom_label.setMaximumSize(QSize(16777215, 16777215))
        self.thumbnail_zoom_label.setFont(font1)

        self.verticalLayout_2.addWidget(self.thumbnail_zoom_label)

        self.thumbnail_zoom_spinbox = QDoubleSpinBox(self.verticalLayoutWidget_3)
        self.thumbnail_zoom_spinbox.setObjectName(u"thumbnail_zoom_spinbox")
        self.thumbnail_zoom_spinbox.setEnabled(False)
        sizePolicy6.setHeightForWidth(self.thumbnail_zoom_spinbox.sizePolicy().hasHeightForWidth())
        self.thumbnail_zoom_spinbox.setSizePolicy(sizePolicy6)
        self.thumbnail_zoom_spinbox.setMaximumSize(QSize(160, 16777215))
        self.thumbnail_zoom_spinbox.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.thumbnail_zoom_spinbox.setAccelerated(True)
        self.thumbnail_zoom_spinbox.setDecimals(3)
        self.thumbnail_zoom_spinbox.setMinimum(1.000000000000000)
        self.thumbnail_zoom_spinbox.setMaximum(1.000000000000000)
        self.thumbnail_zoom_spinbox.setSingleStep(0.001000000000000)
        self.thumbnail_zoom_spinbox.setValue(1.000000000000000)

        self.verticalLayout_2.addWidget(self.thumbnail_zoom_spinbox)

        self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.image_edit_scroll_area.setWidget(self.image_edit_area_widget_properties)

        self.load_buttons_box.addWidget(self.image_edit_scroll_area)

        self.image_tab_vertical_layout = QVBoxLayout()
        self.image_tab_vertical_layout.setSpacing(5)
        self.image_tab_vertical_layout.setObjectName(u"image_tab_vertical_layout")
        self.copy_to_clipboard_button = QPushButton(self.grid)
        self.copy_to_clipboard_button.setObjectName(u"copy_to_clipboard_button")
        sizePolicy.setHeightForWidth(self.copy_to_clipboard_button.sizePolicy().hasHeightForWidth())
        self.copy_to_clipboard_button.setSizePolicy(sizePolicy)
        self.copy_to_clipboard_button.setMaximumSize(QSize(195, 16777215))
        self.copy_to_clipboard_button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.image_tab_vertical_layout.addWidget(self.copy_to_clipboard_button)

        self.export_thumbnail_button = QPushButton(self.grid)
        self.export_thumbnail_button.setObjectName(u"export_thumbnail_button")
        sizePolicy.setHeightForWidth(self.export_thumbnail_button.sizePolicy().hasHeightForWidth())
        self.export_thumbnail_button.setSizePolicy(sizePolicy)
        self.export_thumbnail_button.setMaximumSize(QSize(195, 16777215))
        self.export_thumbnail_button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.image_tab_vertical_layout.addWidget(self.export_thumbnail_button)

        self.export_logo_button = QPushButton(self.grid)
        self.export_logo_button.setObjectName(u"export_logo_button")
        sizePolicy.setHeightForWidth(self.export_logo_button.sizePolicy().hasHeightForWidth())
        self.export_logo_button.setSizePolicy(sizePolicy)
        self.export_logo_button.setMaximumSize(QSize(195, 16777215))
        self.export_logo_button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.image_tab_vertical_layout.addWidget(self.export_logo_button)

        self.export_background_jacket_button = QPushButton(self.grid)
        self.export_background_jacket_button.setObjectName(u"export_background_jacket_button")
        sizePolicy.setHeightForWidth(self.export_background_jacket_button.sizePolicy().hasHeightForWidth())
        self.export_background_jacket_button.setSizePolicy(sizePolicy)
        self.export_background_jacket_button.setMaximumSize(QSize(195, 16777215))
        self.export_background_jacket_button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.image_tab_vertical_layout.addWidget(self.export_background_jacket_button)

        self.generate_spr_db_button = QPushButton(self.grid)
        self.generate_spr_db_button.setObjectName(u"generate_spr_db_button")
        self.generate_spr_db_button.setMaximumSize(QSize(195, 16777215))
        self.generate_spr_db_button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.image_tab_vertical_layout.addWidget(self.generate_spr_db_button)


        self.load_buttons_box.addLayout(self.image_tab_vertical_layout)


        self.horizontalLayout_5.addLayout(self.load_buttons_box)

        MainWindow.setCentralWidget(self.grid)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        self.ft_song_selector_preview.setText("")
        self.mm_result_preview.setText("")
        self.mm_song_selector_preview.setText("")
        self.ft_result_preview.setText("")
        self.load_background_button.setText(QCoreApplication.translate("MainWindow", u"Load Background", None))
        self.load_logo_button.setText(QCoreApplication.translate("MainWindow", u"Load Logo", None))
        self.load_thumbnail_button.setText(QCoreApplication.translate("MainWindow", u"Load Thumbnail", None))
        self.load_jacket_button.setText(QCoreApplication.translate("MainWindow", u"Load Jacket", None))
        self.has_logo_checkbox.setText(QCoreApplication.translate("MainWindow", u"Has logo?", None))
        self.new_classics_checkbox.setText(QCoreApplication.translate("MainWindow", u"New Classics?", None))
        self.jacket_horizontal_offset_label.setText(QCoreApplication.translate("MainWindow", u"Jacket Horizontal Offset", None))
        self.jacket_vertical_offset_label.setText(QCoreApplication.translate("MainWindow", u"Jacket Vertical Offset", None))
        self.jacket_rotation_label.setText(QCoreApplication.translate("MainWindow", u"Jacket Rotation", None))
        self.jacket_rotation_spinbox.setSuffix(QCoreApplication.translate("MainWindow", u"\u00b0", None))
        self.jacket_zoom_label.setText(QCoreApplication.translate("MainWindow", u"Jacket Zoom", None))
        self.jacket_zoom_spinbox.setSuffix(QCoreApplication.translate("MainWindow", u"x", None))
        self.background_horizontal_offset_label.setText(QCoreApplication.translate("MainWindow", u"Background Horizontal Offset", None))
        self.background_vertical_offset_label.setText(QCoreApplication.translate("MainWindow", u"Background Vertical Offset", None))
        self.background_rotation_label.setText(QCoreApplication.translate("MainWindow", u"Background Rotation", None))
        self.background_rotation_spinbox.setSuffix(QCoreApplication.translate("MainWindow", u"\u00b0", None))
        self.background_zoom_label.setText(QCoreApplication.translate("MainWindow", u"Background Zoom", None))
        self.background_zoom_spinbox.setSuffix(QCoreApplication.translate("MainWindow", u"x", None))
        self.logo_horizontal_offset_label.setText(QCoreApplication.translate("MainWindow", u"Logo Horizontal Offset", None))
        self.logo_vertical_offset_label.setText(QCoreApplication.translate("MainWindow", u"Logo Vertical Offset", None))
        self.logo_rotation_label.setText(QCoreApplication.translate("MainWindow", u"Logo Rotation", None))
        self.logo_rotation_spinbox.setSuffix(QCoreApplication.translate("MainWindow", u"\u00b0", None))
        self.logo_zoom_label.setText(QCoreApplication.translate("MainWindow", u"Logo Zoom", None))
        self.logo_zoom_spinbox.setSuffix(QCoreApplication.translate("MainWindow", u"x", None))
        self.thumbnail_horizontal_offset_label.setText(QCoreApplication.translate("MainWindow", u"Thumbnail Horizontal Offset", None))
        self.thumbnail_vertical_offset_label.setText(QCoreApplication.translate("MainWindow", u"Thumbnail Vertical Offset", None))
        self.thumbnail_rotation_label.setText(QCoreApplication.translate("MainWindow", u"Thumbnail Rotation", None))
        self.thumbnail_rotation_spinbox.setSuffix(QCoreApplication.translate("MainWindow", u"\u00b0", None))
        self.thumbnail_zoom_label.setText(QCoreApplication.translate("MainWindow", u"Thumbnail Zoom", None))
        self.thumbnail_zoom_spinbox.setSuffix(QCoreApplication.translate("MainWindow", u"x", None))
        self.copy_to_clipboard_button.setText(QCoreApplication.translate("MainWindow", u"Copy preview to clipboard", None))
        self.export_thumbnail_button.setText(QCoreApplication.translate("MainWindow", u"Export Thumbnail", None))
        self.export_logo_button.setText(QCoreApplication.translate("MainWindow", u"Export Logo", None))
        self.export_background_jacket_button.setText(QCoreApplication.translate("MainWindow", u"Export Background/Jacket", None))
        self.generate_spr_db_button.setText(QCoreApplication.translate("MainWindow", u"Generate Sprite Database", None))
        pass
    # retranslateUi

