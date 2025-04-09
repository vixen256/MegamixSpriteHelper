from pathlib import Path, PurePath
import sys
from time import sleep

import filedialpy
from PySide6.QtCore import Qt, Slot, QFileSystemWatcher, QSize
from PySide6.QtWidgets import QApplication, QLabel, QMessageBox, QSizePolicy, QMainWindow
from PySide6.QtGui import QPixmap
from PIL import Image, ImageOps, ImageQt
from PIL.Image import Resampling
from copykitten import copy_image
from filedialpy import openFile

import numpy as np
from scipy.ndimage import distance_transform_edt

from ui_SpriteHelper import Ui_MainWindow
from SceneComposer import SceneComposer

class Configurable:
    def __init__(self):
        self.script_directory = Path.cwd()
        self.allowed_file_types = ["*.png *.jpg"]

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

def check_for_files():
    missing_files = []
    required_files = [
        config.script_directory / 'Images/Dummy/Thumbnail-Mask.png',
        config.script_directory / 'Images/Dummy/Jacketfix-Jacket-Mask.png',
        config.script_directory / 'Images/Dummy/Jacketfix-Background-Mask.png',
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
        self.jacket_post_processing()
        self.background_post_processing()
        self.thumbnail_post_processing()
        self.logo_post_processing()

        #Start watching for file updates of loaded files
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
        self.main_box.export_logo_button.clicked.connect(self.export_logo_button_callback)

        #Connect spinboxes with functions that update their sprites
        self.spinbox_editing_finished_trigger("on")

        #Connect checkboxes with their functions
        self.main_box.has_logo_checkbox.checkStateChanged.connect(self.has_logo_checkbox_callback)

        self.draw_image_grid()

    def resizeEvent(self,event):
        # Force 2:1 aspect ratio
        new_width = self.size().width()
        new_height = int(new_width / 2)
        size = QSize(new_width,new_height)
        self.resize(size)

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
    def jacket_spinbox_values_reset(self):
        self.spinbox_editing_finished_trigger("off")

        self.main_box.jacket_rotation_spinbox.setValue(0)
        self.main_box.jacket_horizontal_offset_spinbox.setValue(0)
        self.main_box.jacket_vertical_offset_spinbox.setValue(0)
        self.main_box.jacket_zoom_spinbox.setValue(1.00)

        self.spinbox_editing_finished_trigger("on")

    def logo_spinbox_values_reset(self):
        self.spinbox_editing_finished_trigger("off")

        self.main_box.logo_rotation_spinbox.setValue(0)
        self.main_box.logo_horizontal_offset_spinbox.setValue(0)
        self.main_box.logo_vertical_offset_spinbox.setValue(0)
        self.main_box.logo_zoom_spinbox.setValue(1.00)

        self.spinbox_editing_finished_trigger("on")

    def background_spinbox_values_reset(self):
        self.spinbox_editing_finished_trigger("off")

        self.main_box.background_rotation_spinbox.setValue(0)
        self.main_box.background_horizontal_offset_spinbox.setValue(0)
        self.main_box.background_vertical_offset_spinbox.setValue(0)
        self.main_box.background_zoom_spinbox.setValue(1.00)

        self.spinbox_editing_finished_trigger("on")

    def thumbnail_spinbox_values_reset(self):
        self.spinbox_editing_finished_trigger("off")

        self.main_box.thumbnail_rotation_spinbox.setValue(0)
        self.main_box.thumbnail_horizontal_offset_spinbox.setValue(0)
        self.main_box.thumbnail_vertical_offset_spinbox.setValue(0)
        self.main_box.thumbnail_zoom_spinbox.setValue(1.00)

        self.spinbox_editing_finished_trigger("on")

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

    def watcher_file_modified_action(self,path):
        sleep(2) #TODO replace sleep with detection is the modified file there
        self.watcher.removePath(path)
        self.reload_images()
        self.watcher.addPath(path)
        self.draw_image_grid()
    def reload_images(self):
        self.background_post_processing()
        self.jacket_post_processing()
        self.logo_post_processing()
        self.thumbnail_post_processing()
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
        self.main_box.jacket_horizontal_offset_spinbox.setRange((jacket_scaled.width * -1) + 502, 0)
        self.main_box.jacket_vertical_offset_spinbox.setRange((jacket_scaled.height * -1) + 502, 0)
        #TODO Fix zoom
    @Slot()
    def logo_post_processing(self):
        print("logo")
        if self.main_box.has_logo_checkbox.checkState() == Qt.CheckState.Checked:
            logo_rotation = self.main_box.logo_rotation_spinbox.value()
            logo_vertical_translate = self.main_box.logo_vertical_offset_spinbox.value()
            logo_horizontal_translate = self.main_box.logo_horizontal_offset_spinbox.value()
            logo_zoom = self.main_box.logo_zoom_spinbox.value()
            logo_base = Image.new('RGBA', (870, 330))

            self.logo_image = Image.open(self.logo_location).convert('RGBA')
            logo_rotated = self.logo_image.rotate(logo_rotation, Resampling.BILINEAR, expand=True)
            logo_scaled = ImageOps.scale(logo_rotated, logo_zoom)
            logo_base.alpha_composite(logo_scaled, (logo_horizontal_translate, logo_vertical_translate))

            SceneComposer.logo = logo_base

            self.main_box.logo_horizontal_offset_spinbox.setRange((logo_scaled.width * -1) + 435,logo_scaled.width - 435)
            self.main_box.logo_vertical_offset_spinbox.setRange((logo_scaled.height * -1) + 150,logo_scaled.height - 150)
        else:
            SceneComposer.logo = Image.new('RGBA', (870, 330))

        #TODO Fix zoom
    @Slot()
    def background_post_processing(self):
        print("background")
        background_rotation = self.main_box.background_rotation_spinbox.value()
        background_vertical_translate = self.main_box.background_vertical_offset_spinbox.value()
        background_horizontal_translate = self.main_box.background_horizontal_offset_spinbox.value()
        background_zoom = self.main_box.background_zoom_spinbox.value()
        background_base = Image.new('RGBA', (1280, 720))

        self.background_image = Image.open(self.background_location).convert('RGBA')
        background_rotated = self.background_image.rotate(background_rotation, Resampling.BILINEAR, expand=True)
        background_scaled = ImageOps.scale(background_rotated, background_zoom)
        background_base.alpha_composite(background_scaled, (background_horizontal_translate,background_vertical_translate,))
        SceneComposer.scaled_background = ImageOps.scale(background_base,1.5)

        self.main_box.background_horizontal_offset_spinbox.setRange((background_scaled.width * -1) + 1280, 0)
        self.main_box.background_vertical_offset_spinbox.setRange((background_scaled.height * -1) + 720, 0)
        #TODO Fix zoom
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

        self.thumbnail_image = Image.open(self.thumbnail_location).convert('RGBA')
        thumbnail_rotated = self.thumbnail_image.rotate(thumbnail_rotation, Resampling.BILINEAR, expand=True)
        thumbnail_scaled = ImageOps.scale(thumbnail_rotated, thumbnail_zoom)
        thumbnail_base.alpha_composite(thumbnail_scaled,(thumbnail_horizontal_translate,thumbnail_vertical_translate))
        thumbnail_base = Image.composite(thumbnail_base,thumbnail_empty,mask)
        SceneComposer.thumbnail = thumbnail_base

        self.main_box.thumbnail_horizontal_offset_spinbox.setRange((thumbnail_scaled.width * -1) +128,27)
        self.main_box.thumbnail_vertical_offset_spinbox.setRange((thumbnail_scaled.height * -1) + 64,0)
        #TODO Fix zoom


    @Slot()
    def has_logo_checkbox_callback(self):
        if self.main_box.has_logo_checkbox.checkState() == Qt.CheckState.Checked:
            #Make options to tweak logo visible
            self.main_box.logo_horizontal_offset_label.setEnabled(True)
            self.main_box.logo_horizontal_offset_spinbox.setEnabled(True)
            self.main_box.logo_vertical_offset_label.setEnabled(True)
            self.main_box.logo_vertical_offset_spinbox.setEnabled(True)
            self.main_box.logo_rotation_label.setEnabled(True)
            self.main_box.logo_rotation_spinbox.setEnabled(True)
            self.main_box.logo_zoom_label.setEnabled(True)
            self.main_box.logo_zoom_spinbox.setEnabled(True)
            #Enable buttons related to logos
            self.main_box.load_logo_button.setEnabled(True)
            self.main_box.export_logo_button.setEnabled(True)
            #Draw Logo
            self.logo_post_processing()
            self.draw_image_grid()
        else:
            # Make options to tweak logo invisible
            self.main_box.logo_horizontal_offset_label.setDisabled(True)
            self.main_box.logo_horizontal_offset_spinbox.setDisabled(True)
            self.main_box.logo_vertical_offset_label.setDisabled(True)
            self.main_box.logo_vertical_offset_spinbox.setDisabled(True)
            self.main_box.logo_rotation_label.setDisabled(True)
            self.main_box.logo_rotation_spinbox.setDisabled(True)
            self.main_box.logo_zoom_label.setDisabled(True)
            self.main_box.logo_zoom_spinbox.setDisabled(True)
            #Disable buttons related to logos
            self.main_box.load_logo_button.setDisabled(True)
            self.main_box.export_logo_button.setDisabled(True)
            # Hide Logo
            self.logo_post_processing()
            self.draw_image_grid()
    @Slot()
    def load_background_button_callback(self):
        open_background = openFile(title="Open background image", filter=config.allowed_file_types)

        if open_background == '':
            print("Background image wasn't chosen")
        else:
            self.watcher.removePath(str(self.background_location))
            self.background_location = open_background
            self.watcher.addPath(str(self.background_location))
            self.background_spinbox_values_reset()
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
            self.jacket_spinbox_values_reset()
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
            self.logo_spinbox_values_reset()
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
            self.thumbnail_spinbox_values_reset()
            self.thumbnail_post_processing()
            self.draw_image_grid()
    @Slot()
    def export_background_jacket_button_callback(self):
        jacket_mask = Image.open(config.script_directory / 'Images/Dummy/Jacketfix-Jacket-Mask.png').convert('L')
        background_mask = Image.open(config.script_directory / 'Images/Dummy/Jacketfix-Background-Mask.png').convert('L')

        jacket_composite = Image.new('RGBA', (2048, 1024), (0, 0, 0, 0))
        jacket_composite.alpha_composite(SceneComposer.jacket, (1286, 2), (0, 0, 502, 502))
        jacket_composite = fill_transparent_pixels(jacket_composite)
        jacket_composite.putalpha(jacket_mask)

        background_composite = Image.new('RGBA', (2048, 1024), (0, 0, 0, 0))
        background_composite.alpha_composite(self.background_image,(2,2),(0,0,1280,720))
        background_composite = fill_transparent_pixels(background_composite)
        background_composite.putalpha(background_mask)

        composite = Image.new('RGBA',(2048,1024))
        composite.alpha_composite(background_composite)
        composite.alpha_composite(jacket_composite)


        save_location = filedialpy.saveFile(initial_file="Background Texture.png", filter="*.png")
        composite.save(save_location,"png")
    @Slot()
    def export_thumbnail_button_callback(self):
        composite = Image.new('RGBA',(128,64))
        composite.alpha_composite(SceneComposer.thumbnail)

        save_location = filedialpy.saveFile(initial_file="Thumbnail Texture.png", filter="*.png")
        composite.save(save_location, "png")
    @Slot()
    def export_logo_button_callback(self):
        composite = Image.new('RGBA',(870,330))
        composite.alpha_composite(SceneComposer.logo)

        save_location = filedialpy.saveFile(initial_file="Logo Texture.png", filter="*.png")
        composite.save(save_location, "png")

if __name__ == "__main__":
    config = Configurable()
    SceneComposer = SceneComposer()
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    app.exec()