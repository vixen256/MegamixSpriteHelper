from pathlib import Path, PurePath
import sys
from time import sleep

import PIL.Image
import filedialpy
from PySide6.QtCore import Qt, Slot, QSize, QMetaObject, QCoreApplication, QFileSystemWatcher
from PySide6.QtWidgets import QApplication, QPushButton, QDialog, QHBoxLayout, QVBoxLayout, QLabel, QSpacerItem, \
    QGridLayout, QMessageBox, QSizePolicy, QWidget, QLayout, QMainWindow
from PySide6.QtGui import QPixmap, QImage, QPicture, QScreen
from PIL import Image, ImageOps, ImageQt
from PIL.Image import Resampling
from copykitten import copy_image
from filedialpy import openFile

import numpy as np
from scipy.ndimage import distance_transform_edt

from ui_SpriteHelper import Ui_MainWindow


class Configurable:
    def __init__(self):
        self.script_directory = Path.cwd()
        self.allowed_file_types = ["*.png *.jpg"]
        self.image_scaling_behaviour = QSizePolicy.Policy.Ignored

class SceneComposer:
    def compose_scene(self,ui_screen):
        self.prepare_scene(ui_screen)
        composite = Image.new('RGBA' ,(1920,1080))
        iteration=0
        for layer in self.grab_layers(ui_screen):
            composite.alpha_composite(layer,self.anchor_points[iteration])
            iteration=iteration+1
        return composite

    def prepare_scene(self,ui_screen):
        match ui_screen:
            case "mm_song_selector":
                # Anchor points and tweaks
                self.mm_song_selector_jacket_anchor_point = (1284, 130)
                mm_song_selector_jacket_angle = -7
                self.rotated_jacket = self.jacket.rotate(mm_song_selector_jacket_angle, Resampling.BILINEAR, expand=True)

                self.mm_song_selector_logo_anchor_point = (825, 537)
                mm_song_selector_logo_scale = 0.8
                self.scaled_logo = ImageOps.scale(self.logo, mm_song_selector_logo_scale)

                mm_song_selector_thumbnail_size = (160, 76)
                mm_song_selector_selected_thumbnail_size = (202, 98)
                self.resized_thumbnail = self.thumbnail.resize(mm_song_selector_thumbnail_size,resample=Resampling.BILINEAR)
                self.resized_selected_thumbnail = self.thumbnail.resize(mm_song_selector_selected_thumbnail_size,resample=Resampling.BILINEAR)

                self.mm_song_selector_thumbnail_1_anchor_point = (-98, -24)
                self.mm_song_selector_thumbnail_2_anchor_point = (-66, 90)
                self.mm_song_selector_thumbnail_3_anchor_point = (-34, 204)
                self.mm_song_selector_selected_thumbnail_anchor_point = (-8, 332)
                self.mm_song_selector_thumbnail_4_anchor_point = (44, 476)
                self.mm_song_selector_thumbnail_5_anchor_point = (108, 704)
                self.mm_song_selector_thumbnail_6_anchor_point = (140, 818)
                self.mm_song_selector_thumbnail_7_anchor_point = (168, 943)

                # Load images needed
                self.backdrop = Image.open(config.script_directory / 'Images/MM UI - Song Select/Backdrop.png').convert('RGBA')
                self.song_selector = Image.open(config.script_directory / 'Images/MM UI - Song Select/Song Selector.png').convert('RGBA')
                self.middle_layer = Image.open(config.script_directory / 'Images/MM UI - Song Select/Middle Layer.png').convert('RGBA')
                self.top_layer = Image.open(config.script_directory / 'Images/MM UI - Song Select/Top Layer.png').convert('RGBA')
            case "mm_result":
                # Anchor points and tweaks
                self.mm_result_jacket_anchor_point = (108, 387)
                mm_result_jacket_angle = -7
                mm_result_jacket_scale = (0.9)
                scaled_jacket = ImageOps.scale(self.jacket, mm_result_jacket_scale)
                self.rotated_jacket = scaled_jacket.rotate(mm_result_jacket_angle, Resampling.BILINEAR, expand=True)

                self.mm_result_logo_anchor_point = (67, 784)
                mm_result_logo_scale = (0.7)
                self.scaled_logo = ImageOps.scale(self.logo, mm_result_logo_scale)

                # Load images needed
                self.backdrop = ImageOps.scale(Image.open((config.script_directory / 'Images/Dummy/SONG_BG_DUMMY.png')), 1.5)
                self.middle_layer = Image.open((config.script_directory / 'Images/MM UI - Results Screen/Middle Layer.png'))
                self.top_layer = Image.open((config.script_directory / 'Images/MM UI - Results Screen/Top Layer.png'))

            case "ft_song_selector":
                # Anchor points and tweaks
                self.ft_song_selector_jacket_anchor_point = (1331, 205)
                ft_song_selector_jacket_scale = (0.97)
                ft_song_selector_jacket_angle = 5
                scaled_jacket = ImageOps.scale(self.jacket, ft_song_selector_jacket_scale)
                self.rotated_jacket = scaled_jacket.rotate(ft_song_selector_jacket_angle, Resampling.BILINEAR, expand=True)

                self.ft_song_selector_logo_anchor_point = (803, 515)
                ft_song_selector_logo_scale = (0.9)
                self.scaled_logo = ImageOps.scale(self.logo, ft_song_selector_logo_scale)

                # Load images needed
                self.backdrop = Image.open((config.script_directory / 'Images/FT UI - Song Select/Base.png'))
                self.middle_layer = Image.open((config.script_directory / 'Images/FT UI - Song Select/Middle Layer.png'))
                self.top_layer = Image.open((config.script_directory / 'Images/FT UI - Song Select/Top Layer.png'))

            case "ft_result":
                # Anchor points and tweaks
                self.ft_result_jacket_anchor_point = (164, 303)
                ft_result_jacket_angle = 5
                self.rotated_jacket = self.jacket.rotate(ft_result_jacket_angle, Resampling.BILINEAR, expand=True)

                self.ft_result_logo_anchor_point = (134, 663)
                ft_result_logo_scale = (0.75)
                self.scaled_logo = ImageOps.scale(self.logo, ft_result_logo_scale)

                self.backdrop = Image.open((config.script_directory / 'Images/FT UI - Results Screen/Base.png'))
                self.middle_layer = Image.open((config.script_directory / 'Images/FT UI - Results Screen/Middle Layer.png'))
                self.top_layer = Image.open((config.script_directory / 'Images/FT UI - Results Screen/Top Layer.png'))

        pass
    def grab_layers(self,ui_screen):
        match ui_screen:
            case "mm_song_selector":
                self.anchor_points = (
                    (0,0),
                    (0,0),
                    self.mm_song_selector_jacket_anchor_point,
                    (0,0),
                    self.mm_song_selector_logo_anchor_point,
                    (0,0),
                    self.mm_song_selector_thumbnail_1_anchor_point,
                    self.mm_song_selector_thumbnail_2_anchor_point,
                    self.mm_song_selector_thumbnail_3_anchor_point,
                    self.mm_song_selector_selected_thumbnail_anchor_point,
                    self.mm_song_selector_thumbnail_4_anchor_point,
                    self.mm_song_selector_thumbnail_5_anchor_point,
                    self.mm_song_selector_thumbnail_6_anchor_point,
                    self.mm_song_selector_thumbnail_7_anchor_point,
                    (0,0)

                )
                return (
                    self.backdrop,
                    self.scaled_background,
                    self.rotated_jacket,
                    self.middle_layer,
                    self.scaled_logo,
                    self.song_selector,
                    self.resized_thumbnail,
                    self.resized_thumbnail,
                    self.resized_thumbnail,
                    self.resized_selected_thumbnail,
                    self.resized_thumbnail,
                    self.resized_thumbnail,
                    self.resized_thumbnail,
                    self.resized_thumbnail,
                    self.top_layer
                )
            case "mm_result":
                self.anchor_points = (
                    (0,0),
                    (0,0),
                    (0,0),
                    self.mm_result_jacket_anchor_point,
                    self.mm_result_logo_anchor_point,
                    (0,0)
                )
                return (
                    self.backdrop,
                    self.scaled_background,
                    self.middle_layer,
                    self.rotated_jacket,
                    self.scaled_logo,
                    self.top_layer
                )
            case "ft_song_selector":
                self.anchor_points = (
                    (0,0),
                    (0,0),
                    (0,0),
                    self.ft_song_selector_jacket_anchor_point,
                    self.ft_song_selector_logo_anchor_point,
                    (0,0)
                )
                return (
                    self.backdrop,
                    self.scaled_background,
                    self.middle_layer,
                    self.rotated_jacket,
                    self.scaled_logo,
                    self.top_layer
                )
            case "ft_result":
                self.anchor_points = (
                    (0,0),
                    (0,0),
                    self.ft_result_jacket_anchor_point,
                    self.ft_result_logo_anchor_point,
                    (0,0)
                )
                return (
                    self.backdrop,
                    self.middle_layer,
                    self.rotated_jacket,
                    self.scaled_logo,
                    self.top_layer
                )


def fill_transparent_pixels(image):
    img_array = np.array(image)
    if img_array.shape[2] != 4:
        raise ValueError("The image must have an alpha channel.")

    rgb = img_array[..., :3]
    alpha = img_array[..., 3]
    mask = alpha > 0
    if np.all(mask):
        return image

    _, indices = distance_transform_edt(~mask, return_indices=True)
    filled_rgb = rgb[tuple(indices)]
    filled_alpha = np.where(mask, alpha, 255)
    filled_img_array = np.dstack((filled_rgb, filled_alpha)).astype(np.uint8)
    return Image.fromarray(filled_img_array)

def get_scene(ui_scene):
    return QPixmap.fromImage(ImageQt.ImageQt(SceneComposer.compose_scene(ui_scene)))

def find_nearest_16_by_9(w,h) -> (int,int):
    if (h / w) < (16 / 9):
        screen_width, screen_height = 16 * (w // 16), 9 * (w // 16)
    else:
        screen_width, screen_height = 16 * (w // 9), 9 * (w // 9)
    return screen_width, screen_height

def check_for_files():
    missing_files = []
    required_files = [
        config.script_directory / 'Images/Dummy/Thumbnail-Mask.png',
        config.script_directory / 'Images/Dummy/Jacketfix-Mask.png',
        config.script_directory / 'Images/Dummy/SONG_BG_DUMMY.png',
        config.script_directory / 'Images/Dummy/SONG_JK_DUMMY.png',
        config.script_directory / 'Images/Dummy/SONG_LOGO_DUMMY.png',
        config.script_directory / 'Images/Dummy/SONG_JK_THUMBNAIL_DUMMY.png',
        config.script_directory / 'Images/MM UI - Song Select/Backdrop.png',
        config.script_directory / 'Images/MM UI - Song Select/Song Selector.png',
        config.script_directory / 'Images/MM UI - Song Select/Middle Layer.png',
        config.script_directory / 'Images/MM UI - Song Select/Top Layer.png',
        config.script_directory / 'Images/MM UI - Results Screen/Middle Layer.png',
        config.script_directory / 'Images/MM UI - Results Screen/Top Layer.png',
        config.script_directory / 'Images/FT UI - Song Select/Base.png',
        config.script_directory / 'Images/FT UI - Song Select/Middle Layer.png',
        config.script_directory / 'Images/FT UI - Song Select/Top Layer.png',
        config.script_directory / 'Images/FT UI - Results Screen/Base.png',
        config.script_directory / 'Images/FT UI - Results Screen/Middle Layer.png',
        config.script_directory / 'Images/FT UI - Results Screen/Top Layer.png'
    ]

    for file_path in required_files:
        if not file_path.is_file():
            missing_files.append(str(PurePath(file_path.as_posix()).relative_to(config.script_directory.parent))+ "\n")
        else:
            pass
    if not len(missing_files) == 0:
        error_window = QMessageBox()
        error_window.setWindowTitle("Error has occurred!")
        error_window.setText(f"Images are missing:\n{''.join(missing_files)}")
        error_window.exec()
        quit("Images are missing")

@Slot()
def copy_to_clipboard_button_callback():
    composite = Image.new('RGBA', (3840, 2160), (0, 0, 0, 0))
    composite.alpha_composite(SceneComposer.compose_scene("mm_song_selector"), (0, 0))
    composite.alpha_composite(SceneComposer.compose_scene("mm_result"), (1920, 0))
    composite.alpha_composite(SceneComposer.compose_scene("ft_song_selector"), (0, 1080))
    composite.alpha_composite(SceneComposer.compose_scene("ft_result"), (1920, 1080))
    pixels = composite.tobytes()
    copy_image(pixels, composite.width, composite.height)

class MainWindow(QMainWindow):


    def __init__(self):
        super(MainWindow, self).__init__()
        self.main_box = Ui_MainWindow()
        self.main_box.setupUi(self)

        check_for_files()
        #Set default sprites for scenes
        self.background_location = config.script_directory / 'Images/Dummy/SONG_BG_DUMMY.png'
        self.jacket_location = config.script_directory / 'Images/Dummy/SONG_JK_DUMMY.png'
        self.logo_location = config.script_directory / 'Images/Dummy/SONG_LOGO_DUMMY.png'
        self.thumbnail_location = config.script_directory / 'Images/Dummy/SONG_JK_THUMBNAIL_DUMMY.png'
        #Set default values for sprites user can swap
        self.background = Image.open(self.background_location).convert('RGBA')
        SceneComposer.scaled_background = ImageOps.scale(self.background, 1.5).convert('RGBA')
        SceneComposer.jacket = Image.open(self.jacket_location).convert('RGBA')
        SceneComposer.logo = Image.open(self.logo_location).convert('RGBA')
        SceneComposer.thumbnail = Image.open(self.thumbnail_location).convert('RGBA')

        self.watcher = QFileSystemWatcher()
        self.watcher.fileChanged.connect(self.watcher_file_modified_action)
        self.watcher.addPath(str(self.background_location))
        self.watcher.addPath(str(self.jacket_location))
        self.watcher.addPath(str(self.logo_location))
        self.watcher.addPath(str(self.thumbnail_location))

        #Connect buttons with their functionality
        self.main_box.load_background_button.clicked.connect(self.load_background_button_callback)
        self.main_box.load_thumbnail_button.clicked.connect(self.load_thumbnail_button_callback)
        self.main_box.load_logo_button.clicked.connect(self.load_logo_button_callback)
        self.main_box.load_jacket_button.clicked.connect(self.load_jacket_button_callback)
        self.main_box.copy_to_clipboard_button.clicked.connect(copy_to_clipboard_button_callback)
        self.main_box.export_background_jacket_button.clicked.connect(self.export_background_jacket_button_callback)
        self.main_box.export_thumbnail_button.clicked.connect(self.export_thumbnail_button_callback)

        #Connect spinboxes with functions that update their sprites
        self.spinbox_editing_finished_trigger("on")

        self.draw_image_grid()

    def spinbox_editing_finished_trigger(self,state):
        if state == "on":
            self.main_box.jacket_rotation_spinbox.editingFinished.connect(self.jacket_value_edit_trigger)
            self.main_box.jacket_horizontal_offset_spinbox.editingFinished.connect(self.jacket_value_edit_trigger)
            self.main_box.jacket_vertical_offset_spinbox.editingFinished.connect(self.jacket_value_edit_trigger)
            self.main_box.jacket_zoom_spinbox.editingFinished.connect(self.jacket_value_edit_trigger)

            self.main_box.logo_rotation_spinbox.editingFinished.connect(self.logo_value_edit_trigger)
            self.main_box.logo_horizontal_offset_spinbox.editingFinished.connect(self.logo_value_edit_trigger)
            self.main_box.logo_vertical_offset_spinbox.editingFinished.connect(self.logo_value_edit_trigger)
            self.main_box.logo_zoom_spinbox.editingFinished.connect(self.logo_value_edit_trigger)

            self.main_box.background_rotation_spinbox.editingFinished.connect(self.background_value_edit_trigger)
            self.main_box.background_horizontal_offset_spinbox.editingFinished.connect(self.background_value_edit_trigger)
            self.main_box.background_vertical_offset_spinbox.editingFinished.connect(self.background_value_edit_trigger)
            self.main_box.background_zoom_spinbox.editingFinished.connect(self.background_value_edit_trigger)

            self.main_box.thumbnail_rotation_spinbox.editingFinished.connect(self.thumbnail_value_edit_trigger)
            self.main_box.thumbnail_horizontal_offset_spinbox.editingFinished.connect(self.thumbnail_value_edit_trigger)
            self.main_box.thumbnail_vertical_offset_spinbox.editingFinished.connect(self.thumbnail_value_edit_trigger)
            self.main_box.thumbnail_zoom_spinbox.editingFinished.connect(self.thumbnail_value_edit_trigger)

        else:
            self.main_box.jacket_rotation_spinbox.editingFinished.disconnect(self.jacket_value_edit_trigger)
            self.main_box.jacket_horizontal_offset_spinbox.editingFinished.disconnect(self.jacket_value_edit_trigger)
            self.main_box.jacket_vertical_offset_spinbox.editingFinished.disconnect(self.jacket_value_edit_trigger)
            self.main_box.jacket_zoom_spinbox.editingFinished.disconnect(self.jacket_value_edit_trigger)

            self.main_box.logo_rotation_spinbox.editingFinished.disconnect(self.logo_value_edit_trigger)
            self.main_box.logo_horizontal_offset_spinbox.editingFinished.disconnect(self.logo_value_edit_trigger)
            self.main_box.logo_vertical_offset_spinbox.editingFinished.disconnect(self.logo_value_edit_trigger)
            self.main_box.logo_zoom_spinbox.editingFinished.disconnect(self.logo_value_edit_trigger)

            self.main_box.background_rotation_spinbox.editingFinished.disconnect(self.background_value_edit_trigger)
            self.main_box.background_horizontal_offset_spinbox.editingFinished.disconnect(self.background_value_edit_trigger)
            self.main_box.background_vertical_offset_spinbox.editingFinished.disconnect(self.background_value_edit_trigger)
            self.main_box.background_zoom_spinbox.editingFinished.disconnect(self.background_value_edit_trigger)

            self.main_box.thumbnail_rotation_spinbox.editingFinished.disconnect(self.thumbnail_value_edit_trigger)
            self.main_box.thumbnail_horizontal_offset_spinbox.editingFinished.disconnect(self.thumbnail_value_edit_trigger)
            self.main_box.thumbnail_vertical_offset_spinbox.editingFinished.disconnect(self.thumbnail_value_edit_trigger)
            self.main_box.thumbnail_zoom_spinbox.editingFinished.disconnect(self.thumbnail_value_edit_trigger)

    def jacket_value_edit_trigger(self):
        self.jacket_post_processing()
        self.draw_image_grid()

    def logo_value_edit_trigger(self):
        self.logo_post_processing()
        self.draw_image_grid()

    def background_value_edit_trigger(self):
        self.background_post_processing()
        self.draw_image_grid()

    def thumbnail_value_edit_trigger(self):
        self.thumbnail_post_processing()
        self.draw_image_grid()

    def spinbox_values_reset(self):
        self.spinbox_editing_finished_trigger("off")

        self.main_box.jacket_rotation_spinbox.setValue(0)
        self.main_box.jacket_horizontal_offset_spinbox.setValue(0)
        self.main_box.jacket_vertical_offset_spinbox.setValue(0)
        self.main_box.jacket_zoom_spinbox.setValue(1.00)

        self.main_box.logo_rotation_spinbox.setValue(0)
        self.main_box.logo_horizontal_offset_spinbox.setValue(0)
        self.main_box.logo_vertical_offset_spinbox.setValue(0)
        self.main_box.logo_zoom_spinbox.setValue(1.00)

        self.main_box.background_rotation_spinbox.setValue(0)
        self.main_box.background_horizontal_offset_spinbox.setValue(0)
        self.main_box.background_vertical_offset_spinbox.setValue(0)
        self.main_box.background_zoom_spinbox.setValue(1.00)

        self.main_box.thumbnail_rotation_spinbox.setValue(0)
        self.main_box.thumbnail_horizontal_offset_spinbox.setValue(0)
        self.main_box.thumbnail_vertical_offset_spinbox.setValue(0)
        self.main_box.thumbnail_zoom_spinbox.setValue(1.00)

        self.spinbox_editing_finished_trigger("on")

    def reload_images(self):
        self.background_post_processing()
        self.jacket_post_processing()
        self.logo_post_processing()
        self.thumbnail_post_processing()

    def watcher_file_modified_action(self,path):
        sleep(2) #TODO replace sleep with detection is the modified file there
        self.watcher.removePath(path)
        self.reload_images()
        self.watcher.addPath(path)
        self.draw_image_grid()

    def draw_image_grid(self):
        self.mm_song_selector_preview = QLabel(self)
        self.mm_song_selector_preview.setPixmap(
            get_scene("mm_song_selector").scaled(1920,1080,aspectMode=Qt.AspectRatioMode.KeepAspectRatioByExpanding, mode=Qt.TransformationMode.SmoothTransformation))
        self.mm_song_selector_preview.setScaledContents(True)

        self.ft_song_selector_preview = QLabel(self)
        self.ft_song_selector_preview.setPixmap(
            get_scene("ft_song_selector").scaled(1920,1080,aspectMode=Qt.AspectRatioMode.KeepAspectRatioByExpanding, mode=Qt.TransformationMode.SmoothTransformation))
        self.ft_song_selector_preview.setScaledContents(True)

        self.mm_result_preview = QLabel(self)
        self.mm_result_preview.setPixmap(
            get_scene("mm_result").scaled(1920,1080,aspectMode=Qt.AspectRatioMode.KeepAspectRatioByExpanding, mode=Qt.TransformationMode.SmoothTransformation))
        self.mm_result_preview.setScaledContents(True)

        self.ft_result_preview = QLabel(self)
        self.ft_result_preview.setPixmap(
            get_scene("ft_result").scaled(1920,1080,aspectMode=Qt.AspectRatioMode.KeepAspectRatioByExpanding, mode=Qt.TransformationMode.SmoothTransformation))
        self.ft_result_preview.setScaledContents(True)

        self.main_box.image_grid.addWidget(self.mm_song_selector_preview, 0, 0)
        self.main_box.image_grid.addWidget(self.ft_song_selector_preview, 0, 1)
        self.main_box.image_grid.addWidget(self.mm_result_preview, 1, 0)
        self.main_box.image_grid.addWidget(self.ft_result_preview, 1, 1)

    @Slot()
    def jacket_post_processing(self):
        print("jacket")
        jacket_rotation = self.main_box.jacket_rotation_spinbox.value()
        jacket_vertical_translate = self.main_box.jacket_vertical_offset_spinbox.value()
        jacket_horizontal_translate = self.main_box.jacket_horizontal_offset_spinbox.value()
        jacket_zoom = self.main_box.jacket_zoom_spinbox.value()
        jacket_base = Image.new('RGBA',(502,502))

        jacket_image = Image.open(self.jacket_location).convert('RGBA')
        jacket_rotated = jacket_image.rotate(jacket_rotation, Resampling.BILINEAR, expand=True)
        jacket_scaled = ImageOps.scale(jacket_rotated,jacket_zoom)
        jacket_base.alpha_composite(jacket_scaled,(jacket_horizontal_translate,jacket_vertical_translate))

        SceneComposer.jacket = jacket_base


    @Slot()
    def logo_post_processing(self):
        print("logo")
        logo_rotation = self.main_box.logo_rotation_spinbox.value()
        logo_vertical_translate = self.main_box.logo_vertical_offset_spinbox.value()
        logo_horizontal_translate = self.main_box.logo_horizontal_offset_spinbox.value()
        logo_zoom = self.main_box.logo_zoom_spinbox.value()
        logo_base = Image.new('RGBA', (870, 330))

        logo_image = Image.open(self.logo_location).convert('RGBA')
        logo_rotated = logo_image.rotate(logo_rotation, Resampling.BILINEAR, expand=True)
        logo_scaled = ImageOps.scale(logo_rotated, logo_zoom)
        logo_base.alpha_composite(logo_scaled,(logo_horizontal_translate,logo_vertical_translate))

        SceneComposer.logo = logo_base


    @Slot()
    def background_post_processing(self):
        print("background")
        background_rotation = self.main_box.background_rotation_spinbox.value()
        background_vertical_translate = self.main_box.background_vertical_offset_spinbox.value()
        background_horizontal_translate = self.main_box.background_horizontal_offset_spinbox.value()
        background_zoom = self.main_box.background_zoom_spinbox.value()
        background_base = Image.new('RGBA', (1280, 720))

        background_image = Image.open(self.background_location).convert('RGBA')
        background_rotated = background_image.rotate(background_rotation, Resampling.BILINEAR, expand=True)
        background_scaled = ImageOps.scale(background_rotated, background_zoom)
        background_base.alpha_composite(background_scaled, (background_horizontal_translate,background_vertical_translate,))
        SceneComposer.scaled_background = ImageOps.scale(background_base,1.5)


    @Slot()
    def thumbnail_post_processing(self):
        print("thumbnail")
        mask = Image.open(config.script_directory / 'Images/Dummy/Thumbnail-Mask.png').convert('L')
        thumbnail_rotation = self.main_box.thumbnail_rotation_spinbox.value()
        thumbnail_vertical_translate = self.main_box.thumbnail_vertical_offset_spinbox.value()
        thumbnail_horizontal_translate = self.main_box.thumbnail_horizontal_offset_spinbox.value()
        thumbnail_zoom = self.main_box.thumbnail_zoom_spinbox.value()
        thumbnail_empty = Image.new('RGBA', (128, 64))
        thumbnail_base = Image.new('RGBA', (128, 64))

        thumbnail_image = Image.open(self.thumbnail_location).convert('RGBA')
        thumbnail_rotated = thumbnail_image.rotate(thumbnail_rotation, Resampling.BILINEAR, expand=True)
        thumbnail_scaled = ImageOps.scale(thumbnail_rotated, thumbnail_zoom)
        thumbnail_base.alpha_composite(thumbnail_scaled,(thumbnail_horizontal_translate,thumbnail_vertical_translate))
        thumbnail_base = Image.composite(thumbnail_base,thumbnail_empty,mask)
        SceneComposer.thumbnail = thumbnail_base




    @Slot()
    def load_background_button_callback(self):
        open_background = openFile(title="Open background image", filter=config.allowed_file_types)

        if open_background == '':
            print("Background image wasn't chosen")
        else:
            self.watcher.removePath(str(self.background_location))
            self.background_location = open_background
            self.watcher.addPath(str(self.background_location))
            self.spinbox_values_reset()
            self.background_post_processing()
            self.draw_image_grid()

    @Slot()
    def load_jacket_button_callback(self):
        open_jacket = openFile(title="Open jacket image", filter=config.allowed_file_types)

        if open_jacket == '':
            print("Jacket image wasn't chosen")
        else:
            self.watcher.removePath(str(self.jacket_location))
            self.jacket_location = open_jacket
            self.watcher.addPath(str(self.jacket_location))
            self.spinbox_values_reset()
            self.jacket_post_processing()
            self.draw_image_grid()

    @Slot()
    def load_logo_button_callback(self):
        open_logo = openFile(title="Open logo image", filter=config.allowed_file_types)
        if open_logo == '':
            print("Logo image wasn't chosen")
        else:
            self.watcher.removePath(str(self.logo_location))
            self.logo_location = open_logo
            self.watcher.addPath(str(self.logo_location))
            self.spinbox_values_reset()
            self.logo_post_processing()
            self.draw_image_grid()

    @Slot()
    def load_thumbnail_button_callback(self):
        open_thumbnail = openFile(title="Open thumbnail image", filter=config.allowed_file_types)
        if open_thumbnail == '':
            print("Thumbnail image wasn't chosen")
        else:
            self.watcher.removePath(str(self.thumbnail_location))
            self.thumbnail_location = open_thumbnail
            self.watcher.addPath(str(self.thumbnail_location))
            self.spinbox_values_reset()
            self.thumbnail_post_processing()
            self.draw_image_grid()

    @Slot()
    def export_background_jacket_button_callback(self):
        mask = Image.open(config.script_directory / 'Images/Dummy/Jacketfix-Mask.png').convert('L')
        composite = Image.new('RGBA', (2048, 1024), (0, 0, 0, 0))
        composite.alpha_composite(self.background,(2,2),(0,0,1280,720)) #Overlay background and limit it to 1280x720 area
        composite.alpha_composite(SceneComposer.jacket, (1286,2),(0,0,502,502))
        #Extend colors from the edges and then apply mask
        #This fixes jagged edges of the jacket in-game
        composite = fill_transparent_pixels(composite)
        composite.putalpha(mask)

        save_location = filedialpy.saveFile(initial_file="Background Texture.png", filter="*.png")
        composite.save(save_location,"png")

    @Slot()
    def export_thumbnail_button_callback(self):
        composite = Image.new('RGBA',(128,64))
        composite.alpha_composite(SceneComposer.thumbnail)

        save_location = filedialpy.saveFile(initial_file="Thumbnail Texture.png", filter="*.png")
        composite.save(save_location, "png")

if __name__ == "__main__":
    config = Configurable()
    SceneComposer = SceneComposer()
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    app.exec()