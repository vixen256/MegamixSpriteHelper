import tempfile
from pathlib import Path, PurePath
import sys
from time import sleep
from tempfile import mkstemp

import filedialpy
from PySide6.QtCore import Qt, Slot, QFileSystemWatcher, QSize
from PySide6.QtWidgets import QApplication, QLabel, QMessageBox, QSizePolicy, QMainWindow
from PySide6.QtGui import QPixmap
from PIL import Image, ImageOps, ImageQt
from PIL.Image import Resampling
from copykitten import copy_image
from filedialpy import openFile
from decimal import Decimal, getcontext, ROUND_HALF_UP

import numpy as np
from scipy.ndimage import distance_transform_edt

#from FarcCreator import FarcCreator
from ui_SpriteHelper import Ui_MainWindow
from SceneComposer import SceneComposer
from auto_creat_mod_spr_db import Manager, add_farc_to_Manager, read_farc


class Configurable:
    def __init__(self):
        self.script_directory = Path.cwd()
        self.allowed_file_types = ["*.png *.jpg"]
        self.scenes_to_draw = ["mm_song_selector","ft_song_selector","mm_result","ft_result"]

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
def show_message_box(title,contents):
    message_box = QMessageBox()
    message_box.setModal(True)
    message_box.setWindowTitle(title)
    message_box.setText(contents)
    message_box.exec()

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
        self.reload_images()

        #Start watching for file updates of loaded files
        self.watcher = QFileSystemWatcher()
        self.watcher.fileChanged.connect(self.watcher_file_modified_action)
        self.watcher.addPath(str(SceneComposer.background_location))
        self.watcher.addPath(str(SceneComposer.jacket_location))
        self.watcher.addPath(str(SceneComposer.logo_location))
        self.watcher.addPath(str(SceneComposer.thumbnail_location))

        #Connect buttons with their functionality
        self.main_box.load_background_button.clicked.connect(self.load_background_button_callback)
        self.main_box.load_thumbnail_button.clicked.connect(self.load_thumbnail_button_callback)
        self.main_box.load_logo_button.clicked.connect(self.load_logo_button_callback)
        self.main_box.load_jacket_button.clicked.connect(self.load_jacket_button_callback)
        self.main_box.copy_to_clipboard_button.clicked.connect(copy_to_clipboard_button_callback)
        self.main_box.export_background_jacket_button.clicked.connect(self.export_background_jacket_button_callback)
        self.main_box.export_thumbnail_button.clicked.connect(self.export_thumbnail_button_callback)
        self.main_box.export_logo_button.clicked.connect(self.export_logo_button_callback)
        self.main_box.export_bg_jk_logo_farc_button.clicked.connect(self.export_background_jacket_logo_farc_button_callback)
        self.main_box.export_thumbnail_farc_button.clicked.connect(self.export_thumbnail_farc_button_callback)
        self.main_box.generate_spr_db_button.clicked.connect(self.generate_spr_db_button_callback)
        #Connect spinboxes with functions that update their sprites
        self.spinbox_editing_finished_trigger("on")

        #Disable functionality that's not implemented / doesn't work right now
        self.main_box.export_thumbnail_farc_button.setDisabled(True)
        self.main_box.export_bg_jk_logo_farc_button.setDisabled(True)

        #Connect checkboxes with their functions
        self.main_box.has_logo_checkbox.checkStateChanged.connect(self.has_logo_checkbox_callback)

        for scene in config.scenes_to_draw:
            self.draw_image_grid(scene)

    def resizeEvent(self,event):
        # Force 2:1 aspect ratio
        new_width = self.size().width()
        new_height = int(new_width / 2)
        size = QSize(new_width,new_height)
        self.resize(size)

    def draw_image_grid(self,ui_scene):
        match ui_scene:
            case "mm_song_selector":
                self.main_box.mm_song_selector_preview.setPixmap(SceneComposer.compose_scene(ui_scene).toqpixmap())
            case "ft_song_selector":
                self.main_box.ft_song_selector_preview.setPixmap(SceneComposer.compose_scene(ui_scene).toqpixmap())
            case "mm_result":
                self.main_box.mm_result_preview.setPixmap(SceneComposer.compose_scene(ui_scene).toqpixmap())
            case "ft_result":
                self.main_box.ft_result_preview.setPixmap(SceneComposer.compose_scene(ui_scene).toqpixmap())
    def jacket_value_edit_trigger(self):
        SceneComposer.jacket_post_processing(self.main_box.jacket_horizontal_offset_spinbox.value(),self.main_box.jacket_vertical_offset_spinbox.value(),self.main_box.jacket_rotation_spinbox.value(),self.main_box.jacket_zoom_spinbox.value())
        self.change_spinbox_offset_range("jacket")
        for scene in config.scenes_to_draw:
            self.draw_image_grid(scene)
    def logo_value_edit_trigger(self):
        SceneComposer.logo_post_processing(self.main_box.has_logo_checkbox.checkState(),self.main_box.logo_horizontal_offset_spinbox.value(), self.main_box.logo_vertical_offset_spinbox.value(), self.main_box.logo_rotation_spinbox.value(), self.main_box.logo_zoom_spinbox.value())
        self.change_spinbox_offset_range("logo")
        for scene in config.scenes_to_draw:
            self.draw_image_grid(scene)
    def background_value_edit_trigger(self):
        SceneComposer.background_post_processing(self.main_box.background_horizontal_offset_spinbox.value(), self.main_box.background_vertical_offset_spinbox.value(), self.main_box.background_rotation_spinbox.value(), self.main_box.background_zoom_spinbox.value())
        self.change_spinbox_offset_range("background")
        for scene in config.scenes_to_draw:
            self.draw_image_grid(scene)
    def thumbnail_value_edit_trigger(self):
        SceneComposer.thumbnail_post_processing(self.main_box.thumbnail_horizontal_offset_spinbox.value(), self.main_box.thumbnail_vertical_offset_spinbox.value(), self.main_box.thumbnail_rotation_spinbox.value(), self.main_box.thumbnail_zoom_spinbox.value())
        self.change_spinbox_offset_range("thumbnail")
        self.draw_image_grid("mm_song_selector")

    def reload_images(self):
        SceneComposer.background_post_processing(self.main_box.background_horizontal_offset_spinbox.value(), self.main_box.background_vertical_offset_spinbox.value(), self.main_box.background_rotation_spinbox.value(), self.main_box.background_zoom_spinbox.value())
        SceneComposer.jacket_post_processing(self.main_box.jacket_horizontal_offset_spinbox.value(), self.main_box.jacket_vertical_offset_spinbox.value(), self.main_box.jacket_rotation_spinbox.value(), self.main_box.jacket_zoom_spinbox.value())
        SceneComposer.logo_post_processing(self.main_box.has_logo_checkbox.checkState(), self.main_box.logo_horizontal_offset_spinbox.value(), self.main_box.logo_vertical_offset_spinbox.value(), self.main_box.logo_rotation_spinbox.value(), self.main_box.logo_zoom_spinbox.value())
        SceneComposer.thumbnail_post_processing(self.main_box.thumbnail_horizontal_offset_spinbox.value(), self.main_box.thumbnail_vertical_offset_spinbox.value(), self.main_box.thumbnail_rotation_spinbox.value(), self.main_box.thumbnail_zoom_spinbox.value())
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

    def change_spinbox_offset_range(self,spinbox):
        match spinbox:
            case "jacket":
                minimum_horizontal = (SceneComposer.jacket_image.width * -1) + 502
                minimum_vertical = (SceneComposer.jacket_image.height * -1) + 502
                self.main_box.jacket_horizontal_offset_spinbox.setRange(minimum_horizontal, 0)
                self.main_box.jacket_vertical_offset_spinbox.setRange(minimum_vertical, 0)

                if minimum_horizontal == 0:
                    self.main_box.jacket_horizontal_offset_spinbox.setEnabled(False)
                else:
                    self.main_box.jacket_horizontal_offset_spinbox.setEnabled(True)

                if minimum_vertical == 0:
                    self.main_box.jacket_vertical_offset_spinbox.setEnabled(False)
                else:
                    self.main_box.jacket_vertical_offset_spinbox.setEnabled(True)
            case "background":
                minimum_horizontal = (SceneComposer.background_image.width * -1) + 1280
                minimum_vertical = (SceneComposer.background_image.height * -1) + 720
                self.main_box.background_horizontal_offset_spinbox.setRange(minimum_horizontal, 0)
                self.main_box.background_vertical_offset_spinbox.setRange(minimum_vertical, 0)

                if minimum_horizontal == 0:
                    self.main_box.background_horizontal_offset_spinbox.setEnabled(False)
                else:
                    self.main_box.background_horizontal_offset_spinbox.setEnabled(True)

                if minimum_vertical == 0:
                    self.main_box.background_vertical_offset_spinbox.setEnabled(False)
                else:
                    self.main_box.background_vertical_offset_spinbox.setEnabled(True)
            case "logo":
                self.main_box.logo_horizontal_offset_spinbox.setRange((SceneComposer.logo_image.width * -1) + 435,SceneComposer.logo_image.width - 435)
                self.main_box.logo_vertical_offset_spinbox.setRange((SceneComposer.logo_image.height * -1) + 150,SceneComposer.logo_image.height - 150)
            case "thumbnail":
                minimum_horizontal = (SceneComposer.thumbnail_image.width * -1) +128
                minimum_vertical = (SceneComposer.thumbnail_image.height * -1) + 64
                self.main_box.thumbnail_horizontal_offset_spinbox.setRange(minimum_horizontal ,27)
                self.main_box.thumbnail_vertical_offset_spinbox.setRange(minimum_vertical,0)

                if minimum_horizontal == 0:
                    self.main_box.thumbnail_horizontal_offset_spinbox.setEnabled(True)
                else:
                    self.main_box.thumbnail_horizontal_offset_spinbox.setEnabled(True)

                if minimum_vertical == 0:
                    self.main_box.thumbnail_vertical_offset_spinbox.setEnabled(False)
                else:
                    self.main_box.thumbnail_vertical_offset_spinbox.setEnabled(True)

    def change_spinbox_zoom_range(self,spinbox,image_width,image_height):
        match spinbox:
            case "jacket_zoom":
                width_factor =  Decimal(502 / image_width)
                height_factor = Decimal(502 / image_height)
                if width_factor > height_factor:
                    self.main_box.jacket_zoom_spinbox.setEnabled(True)
                    self.main_box.jacket_zoom_spinbox.setRange(width_factor.quantize(Decimal('0.001'),rounding=ROUND_HALF_UP),1.00)
                elif height_factor > width_factor:
                    self.main_box.jacket_zoom_spinbox.setEnabled(True)
                    self.main_box.jacket_zoom_spinbox.setRange(height_factor.quantize(Decimal('0.001'),rounding=ROUND_HALF_UP),1.00)
                elif height_factor == width_factor:
                    self.main_box.jacket_zoom_spinbox.setEnabled(True)
                    self.main_box.jacket_zoom_spinbox.setRange(height_factor,1.00)
                else:
                    self.main_box.jacket_zoom_spinbox.setEnabled(False)
                    self.main_box.jacket_zoom_spinbox.setRange(1.00, 1.00)

            case "background_zoom":
                width_factor = Decimal(1280 / image_width)
                height_factor = Decimal(720 / image_height)
                if width_factor > height_factor:
                    self.main_box.background_zoom_spinbox.setEnabled(True)
                    self.main_box.background_zoom_spinbox.setRange(width_factor.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP), 1.00)
                elif height_factor > width_factor:
                    self.main_box.background_zoom_spinbox.setEnabled(True)
                    self.main_box.background_zoom_spinbox.setRange(height_factor.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP), 1.00)
                elif height_factor == width_factor:
                    self.main_box.background_zoom_spinbox.setEnabled(True)
                    self.main_box.background_zoom_spinbox.setRange(height_factor, 1.00)
                else:
                    self.main_box.background_zoom_spinbox.setEnabled(False)
                    self.main_box.background_zoom_spinbox.setRange(1.00, 1.00)
            case "thumbnail_zoom":
                width_factor = Decimal(128 / image_width)
                height_factor = Decimal(64 / image_height)
                if width_factor > height_factor:
                    self.main_box.thumbnail_zoom_spinbox.setEnabled(True)
                    self.main_box.thumbnail_zoom_spinbox.setRange(width_factor.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP), 1.00)
                elif height_factor > width_factor:
                    self.main_box.thumbnail_zoom_spinbox.setEnabled(True)
                    self.main_box.thumbnail_zoom_spinbox.setRange(height_factor.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP), 1.00)
                elif height_factor == width_factor:
                    self.main_box.thumbnail_zoom_spinbox.setEnabled(True)
                    self.main_box.thumbnail_zoom_spinbox.setRange(height_factor, 1.00)
                else:
                    self.main_box.thumbnail_zoom_spinbox.setEnabled(False)
                    self.main_box.thumbnail_zoom_spinbox.setRange(1.00, 1.00)

    def watcher_file_modified_action(self,path):
        sleep(2) #TODO replace sleep with detection is the modified file there
        self.watcher.removePath(path)
        self.reload_images()
        self.watcher.addPath(path)
        for scene in config.scenes_to_draw:
            self.draw_image_grid(scene)

    def create_background_jacket_texture(self):
        jacket_mask = Image.open(config.script_directory / 'Images/Dummy/Jacketfix-Jacket-Mask.png').convert('L')
        background_mask = Image.open(config.script_directory / 'Images/Dummy/Jacketfix-Background-Mask.png').convert('L')

        jacket_composite = Image.new('RGBA', (2048, 1024), (0, 0, 0, 0))
        jacket_composite.alpha_composite(SceneComposer.jacket, (1286, 2), (0, 0, 502, 502))
        jacket_composite = fill_transparent_pixels(jacket_composite)
        jacket_composite.putalpha(jacket_mask)

        background_composite = Image.new('RGBA', (2048, 1024), (0, 0, 0, 0))
        background_composite.alpha_composite(SceneComposer.background, (2, 2), (0, 0, 1280, 720))
        background_composite = fill_transparent_pixels(background_composite)
        background_composite.putalpha(background_mask)

        background_jacket_texture = Image.new('RGBA', (2048, 1024))
        background_jacket_texture.alpha_composite(background_composite)
        background_jacket_texture.alpha_composite(jacket_composite)
        return background_jacket_texture
    def create_logo_texture(self):
        logo_texture = Image.new('RGBA', (1024, 512))
        logo_texture.alpha_composite(SceneComposer.logo,(2,2))
        return logo_texture
    def create_thumbnail_texture(self):
        thumbnail_texture = Image.new('RGBA', (128, 64))
        thumbnail_texture.alpha_composite(SceneComposer.thumbnail)
        return thumbnail_texture
    def get_song_id(self):
        song_id = int(self.main_box.song_id_spinbox.value())
        if song_id <= 9:
            song_id = f'00{song_id}'
        elif song_id <= 99:
            song_id = f'0{song_id}'
        else:
            song_id = str(song_id)
        return song_id

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
            SceneComposer.logo_post_processing(self.main_box.has_logo_checkbox.checkState(),self.main_box.logo_horizontal_offset_spinbox.value(), self.main_box.logo_vertical_offset_spinbox.value(), self.main_box.logo_rotation_spinbox.value(), self.main_box.logo_zoom_spinbox.value())
            for scene in config.scenes_to_draw:
                self.draw_image_grid(scene)
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
            SceneComposer.logo_post_processing(self.main_box.has_logo_checkbox.checkState(),self.main_box.logo_horizontal_offset_spinbox.value(), self.main_box.logo_vertical_offset_spinbox.value(), self.main_box.logo_rotation_spinbox.value(), self.main_box.logo_zoom_spinbox.value())
            for scene in config.scenes_to_draw:
                self.draw_image_grid(scene)
    @Slot()
    def load_background_button_callback(self):
        open_background = openFile(title="Open background image", filter=config.allowed_file_types)

        if open_background == '':
            print("Background image wasn't chosen")

        elif Image.open(open_background).size < (1280,720):
            show_message_box("Image is too small","Image is too small. Image needs to be at least 1280x720")
        else:
            self.watcher.removePath(str(SceneComposer.background_location))
            SceneComposer.background_location = open_background
            self.change_spinbox_zoom_range("background_zoom", Image.open(open_background).width, Image.open(open_background).height)
            self.watcher.addPath(str(SceneComposer.background_location))
            self.background_spinbox_values_reset()
            SceneComposer.background_post_processing(self.main_box.background_horizontal_offset_spinbox.value(), self.main_box.background_vertical_offset_spinbox.value(), self.main_box.background_rotation_spinbox.value(), self.main_box.background_zoom_spinbox.value())
            self.change_spinbox_offset_range("background")
            for scene in config.scenes_to_draw:
                self.draw_image_grid(scene)
    @Slot()
    def load_jacket_button_callback(self):
        open_jacket = openFile(title="Open jacket image", filter=config.allowed_file_types)

        if open_jacket == '':
            print("Jacket image wasn't chosen")
        elif Image.open(open_jacket).size < (500,500):
            show_message_box("Image is too small", "Image is too small. Image needs to be at least 500x500")
        else:
            self.watcher.removePath(str(SceneComposer.jacket_location))
            SceneComposer.jacket_location = open_jacket
            self.change_spinbox_zoom_range("jacket_zoom", Image.open(open_jacket).width, Image.open(open_jacket).height)
            self.watcher.addPath(str(SceneComposer.jacket_location))
            self.jacket_spinbox_values_reset()
            if Image.open(open_jacket).size in ((500,500),(501,501)):
                print(f"{Image.open(open_jacket).size} jacket loaded.")
                self.change_spinbox_zoom_range("jacket_zoom", 502, 502)
            elif Image.open(open_jacket).width == Image.open(open_jacket).height:
                print(f"Image is {Image.open(open_jacket).width}x{Image.open(open_jacket).height}. Imported jacket is 1:1 aspect ratio.")
                zoom = 502 / Image.open(open_jacket).width
                self.main_box.jacket_zoom_spinbox.setValue(zoom)
                print(f"Set jacket's zoom to {zoom}.")
            SceneComposer.jacket_post_processing(self.main_box.jacket_horizontal_offset_spinbox.value(),self.main_box.jacket_vertical_offset_spinbox.value(),self.main_box.jacket_rotation_spinbox.value(),self.main_box.jacket_zoom_spinbox.value())
            self.change_spinbox_offset_range("jacket")
            for scene in config.scenes_to_draw:
                self.draw_image_grid(scene)
    @Slot()
    def load_logo_button_callback(self):
        open_logo = openFile(title="Open logo image", filter=config.allowed_file_types)
        if open_logo == '':
            print("Logo image wasn't chosen")
        elif Image.open(open_logo).size < (435,150):
            show_message_box("Image is too small", "Image is too small. Image needs to be at least 435x150")
        else:
            self.watcher.removePath(str(SceneComposer.logo_location))
            SceneComposer.logo_location = open_logo
            self.watcher.addPath(str(SceneComposer.logo_location))
            self.logo_spinbox_values_reset()
            SceneComposer.logo_post_processing(self.main_box.has_logo_checkbox.checkState(),self.main_box.logo_horizontal_offset_spinbox.value(), self.main_box.logo_vertical_offset_spinbox.value(), self.main_box.logo_rotation_spinbox.value(), self.main_box.logo_zoom_spinbox.value())
            self.change_spinbox_offset_range("logo")
            for scene in config.scenes_to_draw:
                self.draw_image_grid(scene)
    @Slot()
    def load_thumbnail_button_callback(self):
        open_thumbnail = openFile(title="Open thumbnail image", filter=config.allowed_file_types)
        if open_thumbnail == '':
            print("Thumbnail image wasn't chosen")
        elif Image.open(open_thumbnail).size < (100,64):
            show_message_box("Image is too small", "Image is too small. Image needs to be at least 100x64")
        else:
            self.watcher.removePath(str(SceneComposer.thumbnail_location))
            SceneComposer.thumbnail_location = open_thumbnail
            self.change_spinbox_zoom_range("thumbnail_zoom", Image.open(open_thumbnail).width, Image.open(open_thumbnail).height)
            self.watcher.addPath(str(SceneComposer.thumbnail_location))
            self.thumbnail_spinbox_values_reset()
            SceneComposer.thumbnail_post_processing(self.main_box.thumbnail_horizontal_offset_spinbox.value(), self.main_box.thumbnail_vertical_offset_spinbox.value(), self.main_box.thumbnail_rotation_spinbox.value(), self.main_box.thumbnail_zoom_spinbox.value())
            self.change_spinbox_offset_range("thumbnail")
            self.draw_image_grid("mm_song_selector")

    @Slot()
    def export_background_jacket_logo_farc_button_callback(self):
        Image.Image.save(self.create_background_jacket_texture(), (config.script_directory / 'Images/Background Texture.png'))
        Image.Image.save(self.create_logo_texture(), (config.script_directory / 'Images/Logo Texture.png'))
        song_id = self.get_song_id()

        output_location = filedialpy.openDir(title="Select the folder where you want to save Farc file to")
        if output_location == "":
            print("Directory wasn't chosen")
        else:
            output_location = output_location + "/"
            FarcCreator.create_jk_bg_logo_farc(song_id,str(config.script_directory / 'Images/Background Texture.png'),str(config.script_directory / 'Images/Logo Texture.png'),output_location)

        Path.unlink(config.script_directory / 'Images/Background Texture.png',True)
        Path.unlink(config.script_directory / 'Images/Logo Texture.png', True)
    @Slot()
    def export_background_jacket_button_callback(self):
        background_jacket_texture = self.create_background_jacket_texture()
        save_location = filedialpy.saveFile(initial_file="Background Texture.png", filter="*.png")
        background_jacket_texture.save(save_location,"png")
    @Slot()
    def export_thumbnail_button_callback(self):
        thumbnail_texture = self.create_thumbnail_texture()
        save_location = filedialpy.saveFile(initial_file="Thumbnail Texture.png", filter="*.png")
        thumbnail_texture.save(save_location, "png")
    @Slot()
    def export_thumbnail_farc_button_callback(self):
        Image.Image.save(self.create_thumbnail_texture(),(config.script_directory / 'Images/Thumbnail Texture.png'))
        song_id = self.get_song_id()

        output_location = filedialpy.openDir(title="Select the folder where you want to save Farc file to")
        if output_location == "":
            print("Directory wasn't chosen")
        else:
            output_location = output_location + "/"
            FarcCreator.create_thumbnail_farc(song_id,str(config.script_directory / 'Images/Thumbnail Texture.png'),output_location)

        Path.unlink(config.script_directory / 'Images/Thumbnail Texture.png', True)
    @Slot()
    def export_logo_button_callback(self):
        logo_texture = self.create_logo_texture()

        save_location = filedialpy.saveFile(initial_file="Logo Texture.png", filter="*.png")
        logo_texture.save(save_location, "png")

    @Slot()
    def generate_spr_db_button_callback(self):
        spr_db = Manager()
        spr_path = filedialpy.openDir(title="Choose 2d folder to generate spr_db for")
        farc_list = []
        if spr_path == "":
            print("Folder wasn't chosen")
        else:
            for spr in Path(spr_path).iterdir():
                _temp_file = Path(spr)
                if _temp_file.suffix.upper() == ".FARC":
                    farc_list.append(_temp_file)
            if len(farc_list) > 0:
                has_old_tmb_farc = False
                has_new_tmb_farc = False
                for farc_file in farc_list:
                    if farc_file.name == "spr_sel_pvtmb.farc":
                        has_old_tmb_farc = True
                    elif farc_file.name[:11] == "spr_sel_tmb":
                        has_new_tmb_farc = True
                if has_new_tmb_farc == True:
                    if has_old_tmb_farc == True:
                        farc_list.remove(Path(spr_path+"/spr_sel_pvtmb.farc"))
                        print("Separate thumbnail farc files found , not including old combined thumbnail farc in generated database!")
                    else:
                        print("Only separate thumbnail farc files found.")
                for farc_file in farc_list:
                    farc_reader = read_farc(farc_file)
                    add_farc_to_Manager(farc_reader, spr_db)
            spr_db.write_db(f'{spr_path}/mod_spr_db.bin')
            print(f"Generated mod_spr_db in {spr_path}")

if __name__ == "__main__":
    config = Configurable()
    SceneComposer = SceneComposer()
    #FarcCreator = FarcCreator()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    main_window = MainWindow()
    main_window.show()

    app.exec()