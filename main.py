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

        SceneComposer.jacket_post_processing(self.main_box.jacket_horizontal_offset_spinbox.value(),self.main_box.jacket_vertical_offset_spinbox.value(),self.main_box.jacket_rotation_spinbox.value(),self.main_box.jacket_zoom_spinbox.value())
        SceneComposer.background_post_processing(self.main_box.background_horizontal_offset_spinbox.value(), self.main_box.background_vertical_offset_spinbox.value(), self.main_box.background_rotation_spinbox.value(), self.main_box.background_zoom_spinbox.value())
        SceneComposer.thumbnail_post_processing(self.main_box.thumbnail_horizontal_offset_spinbox.value(), self.main_box.thumbnail_vertical_offset_spinbox.value(), self.main_box.thumbnail_rotation_spinbox.value(), self.main_box.thumbnail_zoom_spinbox.value())
        SceneComposer.logo_post_processing(self.main_box.has_logo_checkbox.checkState(),self.main_box.logo_horizontal_offset_spinbox.value(), self.main_box.logo_vertical_offset_spinbox.value(), self.main_box.logo_rotation_spinbox.value(), self.main_box.logo_zoom_spinbox.value())

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

        #Connect spinboxes with functions that update their sprites
        self.spinbox_editing_finished_trigger("on")

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
        rendered_preview = QLabel(self)
        rendered_preview.setPixmap(
            QPixmap.fromImage(ImageQt.ImageQt(SceneComposer.compose_scene(ui_scene))).scaled(1920,1080,aspectMode=Qt.AspectRatioMode.KeepAspectRatioByExpanding, mode=Qt.TransformationMode.SmoothTransformation))
        rendered_preview.setScaledContents(True)

        match ui_scene:
            case "mm_song_selector":
                self.main_box.image_grid.addWidget(rendered_preview, 0, 0)
            case "ft_song_selector":
                self.main_box.image_grid.addWidget(rendered_preview, 0, 1)
            case "mm_result":
                self.main_box.image_grid.addWidget(rendered_preview, 1, 0)
            case "ft_result":
                self.main_box.image_grid.addWidget(rendered_preview, 1, 1)

    def jacket_value_edit_trigger(self):
        SceneComposer.jacket_post_processing(self.main_box.jacket_horizontal_offset_spinbox.value(),self.main_box.jacket_vertical_offset_spinbox.value(),self.main_box.jacket_rotation_spinbox.value(),self.main_box.jacket_zoom_spinbox.value())
        for scene in config.scenes_to_draw:
            self.draw_image_grid(scene)
    def logo_value_edit_trigger(self):
        SceneComposer.logo_post_processing(self.main_box.has_logo_checkbox.checkState(),self.main_box.logo_horizontal_offset_spinbox.value(), self.main_box.logo_vertical_offset_spinbox.value(), self.main_box.logo_rotation_spinbox.value(), self.main_box.logo_zoom_spinbox.value())
        for scene in config.scenes_to_draw:
            self.draw_image_grid(scene)
    def background_value_edit_trigger(self):
        SceneComposer.background_post_processing(self.main_box.background_horizontal_offset_spinbox.value(), self.main_box.background_vertical_offset_spinbox.value(), self.main_box.background_rotation_spinbox.value(), self.main_box.background_zoom_spinbox.value())
        for scene in config.scenes_to_draw:
            self.draw_image_grid(scene)
    def thumbnail_value_edit_trigger(self):
        SceneComposer.thumbnail_post_processing(self.main_box.thumbnail_horizontal_offset_spinbox.value(), self.main_box.thumbnail_vertical_offset_spinbox.value(), self.main_box.thumbnail_rotation_spinbox.value(), self.main_box.thumbnail_zoom_spinbox.value())
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

    def watcher_file_modified_action(self,path):
        sleep(2) #TODO replace sleep with detection is the modified file there
        self.watcher.removePath(path)
        self.reload_images()
        self.watcher.addPath(path)
        for scene in config.scenes_to_draw:
            self.draw_image_grid(scene)



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
        else:
            self.watcher.removePath(str(SceneComposer.background_location))
            SceneComposer.background_location = open_background
            self.watcher.addPath(str(SceneComposer.background_location))
            self.background_spinbox_values_reset()
            SceneComposer.background_post_processing(self.main_box.background_horizontal_offset_spinbox.value(), self.main_box.background_vertical_offset_spinbox.value(), self.main_box.background_rotation_spinbox.value(), self.main_box.background_zoom_spinbox.value())
            for scene in config.scenes_to_draw:
                self.draw_image_grid(scene)
    @Slot()
    def load_jacket_button_callback(self):
        open_jacket = openFile(title="Open jacket image", filter=config.allowed_file_types)

        if open_jacket == '':
            print("Jacket image wasn't chosen")
        else:
            self.watcher.removePath(str(SceneComposer.jacket_location))
            SceneComposer.jacket_location = open_jacket
            self.watcher.addPath(str(SceneComposer.jacket_location))
            self.jacket_spinbox_values_reset()
            SceneComposer.jacket_post_processing(self.main_box.jacket_horizontal_offset_spinbox.value(),self.main_box.jacket_vertical_offset_spinbox.value(),self.main_box.jacket_rotation_spinbox.value(),self.main_box.jacket_zoom_spinbox.value())
            for scene in config.scenes_to_draw:
                self.draw_image_grid(scene)
    @Slot()
    def load_logo_button_callback(self):
        open_logo = openFile(title="Open logo image", filter=config.allowed_file_types)
        if open_logo == '':
            print("Logo image wasn't chosen")
        else:
            self.watcher.removePath(str(SceneComposer.logo_location))
            SceneComposer.logo_location = open_logo
            self.watcher.addPath(str(SceneComposer.logo_location))
            self.logo_spinbox_values_reset()
            SceneComposer.logo_post_processing(self.main_box.has_logo_checkbox.checkState(),self.main_box.logo_horizontal_offset_spinbox.value(), self.main_box.logo_vertical_offset_spinbox.value(), self.main_box.logo_rotation_spinbox.value(), self.main_box.logo_zoom_spinbox.value())
            for scene in config.scenes_to_draw:
                self.draw_image_grid(scene)
    @Slot()
    def load_thumbnail_button_callback(self):
        open_thumbnail = openFile(title="Open thumbnail image", filter=config.allowed_file_types)
        if open_thumbnail == '':
            print("Thumbnail image wasn't chosen")
        else:
            self.watcher.removePath(str(SceneComposer.thumbnail_location))
            SceneComposer.thumbnail_location = open_thumbnail
            self.watcher.addPath(str(SceneComposer.thumbnail_location))
            self.thumbnail_spinbox_values_reset()
            SceneComposer.thumbnail_post_processing(self.main_box.thumbnail_horizontal_offset_spinbox.value(), self.main_box.thumbnail_vertical_offset_spinbox.value(), self.main_box.thumbnail_rotation_spinbox.value(), self.main_box.thumbnail_zoom_spinbox.value())
            self.draw_image_grid("mm_song_selector")
    @Slot()
    def export_background_jacket_button_callback(self):
        jacket_mask = Image.open(config.script_directory / 'Images/Dummy/Jacketfix-Jacket-Mask.png').convert('L')
        background_mask = Image.open(config.script_directory / 'Images/Dummy/Jacketfix-Background-Mask.png').convert('L')

        jacket_composite = Image.new('RGBA', (2048, 1024), (0, 0, 0, 0))
        jacket_composite.alpha_composite(SceneComposer.jacket, (1286, 2), (0, 0, 502, 502))
        jacket_composite = fill_transparent_pixels(jacket_composite)
        jacket_composite.putalpha(jacket_mask)

        background_composite = Image.new('RGBA', (2048, 1024), (0, 0, 0, 0))
        background_composite.alpha_composite(SceneComposer.background,(2,2),(0,0,1280,720))
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