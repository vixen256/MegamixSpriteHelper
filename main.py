import io
import math
import os
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from enum import Enum, auto
from pathlib import Path, PurePath
from time import sleep

import PIL.ImageShow
import yaml
from PIL import Image, ImageShow
from PySide6.QtCore import Qt, QFileSystemWatcher, QSize, Signal, QRectF, QStandardPaths, QUrl
from PySide6.QtGui import QPixmap, QPalette, QColor, QImage, QPainter, QGuiApplication, QDesktopServices
from PySide6.QtWidgets import QApplication, QMessageBox, QMainWindow, QWidget, QFileDialog
from wand.image import Image as WImage

from FarcCreator import FarcCreator
from SceneComposer import Scene, QControllableSprites, QPreviewScenes
from auto_creat_mod_spr_db import Manager, add_farc_to_Manager, read_farc
from ui_SpriteHelper import Ui_MainWindow
from ui_ThumbnailIDField import Ui_ThumbnailIDField
from ui_ThumbnailTextureCreator import Ui_ThumbnailTextureCreator
from ui_ThumbnailWidget import Ui_ThumbnailWidget
from widgets import Stylesheet


class OutputTarget(Enum):
    CLIPBOARD = auto()
    IMAGE_VIEWER = auto()
    IMAGE = auto()

class Configurable:
    def __init__(self):
        self.script_directory = Path.cwd()

        extensions = Image.registered_extensions()
        self.readable_extensions = [ext for ext, fmt in extensions.items() if fmt in Image.OPEN]
        formats_string = " ".join(sorted([f"*{ext}" for ext in self.readable_extensions]))

        self.allowed_file_types = f"Image Files ({formats_string})"
        self.scenes_to_draw = [Scene.MEGAMIX_SONG_SELECT,Scene.FUTURE_TONE_SONG_SELECT,Scene.MEGAMIX_RESULT,Scene.FUTURE_TONE_RESULT]
        self.last_used_directory = self.script_directory



class ThumbnailIDFieldWidget(QWidget):
    additionalRequested = Signal(QWidget)
    removeRequested = Signal(QWidget)
    thumb_count_request = Signal()

    def __init__(self,parent=None,variant=False, inferred_id=None):

        super(ThumbnailIDFieldWidget, self).__init__(parent)
        self.variant = variant    #False cannot be removed, spawns with button to add more id fields
                                                #True can be removed, spawns with button to remove itself.

        self.value = None #This should contain Song ID , needs to check if it's under ID limit.
        self.ui = Ui_ThumbnailIDField()
        self.ui.setupUi(self,variant)
        if inferred_id:
            self.ui.song_id_spinbox.setValue(float(inferred_id))
        self.ui.song_id_spinbox.editingFinished.connect(self.thumb_count_request.emit)

        if variant:
            self.ui.id_line_button.clicked.connect(lambda: self.additionalRequested.emit(self))
        else:
            self.ui.id_line_button.clicked.connect(lambda: self.removeRequested.emit(self))




class ThumbnailWidget(QWidget):
    removeRequested = Signal(QWidget)
    thumb_count_request = Signal()

    def __init__(self, parent=None, image_path=None, inferred_id=None):

        super(ThumbnailWidget, self).__init__(parent)

        self.ui = Ui_ThumbnailWidget()
        self.ui.setupUi(self)
        self.ui.remove_thumbnail_button.clicked.connect(self.remove_thumb)
        self.id_field_list = []
        self.image_path = image_path

        id_count = 0
        if inferred_id:
            for i_id in inferred_id:
                if id_count == 0:
                    self.add_id_field(False, i_id=i_id)
                else:
                    self.add_id_field(True , i_id=i_id)
                id_count = id_count + 1
        else:
            self.add_id_field(False)
    def add_id_field(self, can_be_removed=False, i_id=None):
        if can_be_removed:
            id_field = ThumbnailIDFieldWidget(variant=False ,inferred_id = i_id)
        else:
            id_field = ThumbnailIDFieldWidget(variant=True ,inferred_id = i_id)

        id_field.removeRequested.connect(self.remove_id_field)
        id_field.additionalRequested.connect(self.add_id_field)
        id_field.thumb_count_request.connect(lambda: self.thumb_count_request.emit())
        self.id_field_list.append(id_field)
        self.ui.formLayout.addRow(id_field)
        self.thumb_count_request.emit()

    def remove_id_field(self,widget):
        self.ui.formLayout.removeRow(widget)
        self.id_field_list.remove(widget)
        self.thumb_count_request.emit()

    def remove_thumb(self):

        self.removeRequested.emit(self)


def pad_number(number):
    if number >= 100:
        return str(number)
    elif number >= 10:
        return "0"+ str(number)
    else:
        return "00" + str(number)


class ThumbnailWindow(QWidget):
    resized = Signal()
    NameDeleteRequest = Signal()
    def __init__(self):
        super(ThumbnailWindow, self).__init__()
        self.main_box = Ui_ThumbnailTextureCreator()
        self.main_box.setupUi(self)
        self.main_box.load_folder_button.clicked.connect(self.scan_folder_for_thumbnails)
        self.main_box.export_farc_button.clicked.connect(self.create_thumbnail_farc)
        self.main_box.load_image_button.clicked.connect(self.select_file_for_thumbnails)
        self.main_box.load_image_button.clicked.connect(self.update_thumbnail_count_labels)
        self.main_box.delete_all_thumbs_button.clicked.connect(self.delete_all_thumbs)
        self.main_box.mod_name_lineedit.delete_button.clicked.connect(self.delete_selected_name)
        self.thumbnail_widgets = []
        self.resized.connect(self.space_out_thumbnails)
        self.main_box.export_farc_button.setDisabled(True)

        self.id_conflict_palette = QPalette()
        self.id_conflict_palette.setColor(QPalette.ColorRole.Text, QColor(255, 0, 0))

        self.placeholder_palette = QPalette()
        self.placeholder_palette.setColor(QPalette.ColorRole.Text, QColor(170, 170, 170))

        self.auto_filled_palette = QPalette()
        self.auto_filled_palette.setColor(QPalette.ColorRole.Text, QColor(170, 170, 170))

        self.normal_palette = QPalette()
        self.normal_palette.setColor(QPalette.ColorRole.Text, QColor(255,255,255))

        self.known_ids = self.read_saved_ids()

        self.fill_combobox_suggestions()

    def resizeEvent(self,event):
        super().resizeEvent(event)

        self.resized.emit()

    def update_thumbnail_count_labels(self):
        loaded_thumbs = len(self.thumbnail_widgets)
        left_to_fillout = 0

        id_seen = []

        #Gather list of id's, Apply colors
        for thumbnail_widget in self.thumbnail_widgets:
            thumbnail_widget.setStyleSheet("")

            for id_field in thumbnail_widget.id_field_list:
                id_field.setStyleSheet("")
                id_seen.append(id_field.ui.song_id_spinbox.value())
                if  id_field.ui.song_id_spinbox.value() == 0:
                    thumbnail_widget.setStyleSheet(Stylesheet.SCROLL_AREA_UNFILLED.value)
                    id_field.setStyleSheet(Stylesheet.ID_FIELD_PLACEHOLDER.value)
                    left_to_fillout = left_to_fillout + 1

        # Look for conflicts
        duplicates = []
        seen = set()
        #keep only duplicates found
        for i in id_seen:
            if i in seen:
                duplicates.append(i)
            else:
                seen.add(i)

        duplicates = list(filter(lambda a: a != 0, duplicates))

        for thumbnail_widget in self.thumbnail_widgets:
            for id_field in thumbnail_widget.id_field_list:
                if id_field.ui.song_id_spinbox.value() in duplicates:
                    id_field.setPalette(self.id_conflict_palette)
                    id_field.parent().parent().parent().parent().setStyleSheet(Stylesheet.SCROLL_AREA_CONFLICT.value)
                    id_field.setStyleSheet(Stylesheet.ID_FIELD_CONFLICT.value)
                    left_to_fillout = left_to_fillout + 1

        self.main_box.thumbnails_to_fillout_label.setText(f"Thumbnails that need their ID filled out: {left_to_fillout}")
        self.main_box.thumbnails_loaded_label.setText(f"Thumbnails loaded: {loaded_thumbs}")

        if left_to_fillout > 0:
            self.main_box.export_farc_button.setDisabled(True)
            self.main_box.export_farc_button.setToolTip("Please fill out all id fields before exporting FARC file.")
        elif loaded_thumbs == 0:
            self.main_box.export_farc_button.setDisabled(True)
            self.main_box.export_farc_button.setToolTip("")
        else:
            self.main_box.export_farc_button.setDisabled(False)
            self.main_box.export_farc_button.setToolTip("")

    def add_thumbnail(self,image_path,inferred_id):
        if self.thumbnail_widgets:
            for thumbnail in self.thumbnail_widgets:
                if image_path == thumbnail.image_path:
                    return

        thumbnail_widget = ThumbnailWidget(image_path=image_path, inferred_id=inferred_id)


        thumbnail_widget.removeRequested.connect(self.remove_thumbnail_widget)
        thumbnail_widget.thumb_count_request.connect(self.update_thumbnail_count_labels)

        pixmap = QPixmap(image_path)
        thumbnail_widget.ui.thumbnail_image.setPixmap(pixmap)
        thumbnail_widget.ui.thumbnail_image.setScaledContents(True)

        self.main_box.gridLayout.addWidget(thumbnail_widget, 0, 0)
        self.thumbnail_widgets.append(thumbnail_widget)
        return thumbnail_widget

    def infer_thumbnail_id(self,image_path):
        inferred_id_list = []

        for entry in main_window.thumbnail_creator.known_ids:
            if str(image_path) == entry[0]:
                inferred_id_list.append((image_path,entry[1]))
                break

        if not inferred_id_list:
            if Path(image_path).stem.isdigit() and len(Path(image_path).stem) >= 3:
                id_list = [Path(image_path).stem]
                inferred_id_list.append([image_path,id_list])
            else:
                inferred_id_list.append((image_path,[]))
        return inferred_id_list

    def space_out_thumbnails(self):
        width = self.main_box.verticalLayout.geometry().width()
        widget_width = 365
        columns = (width // widget_width) - 1
        x = 0
        y = 0
        for thumbnail in self.thumbnail_widgets:
            self.main_box.gridLayout.removeWidget(thumbnail)

            self.main_box.gridLayout.addWidget(thumbnail,y,x)
            if x == columns:
                y = y + 1
                x = 0
            else:
                x = x + 1
    def read_saved_ids(self):
        if Path('remembered_ids.yaml').exists():
            with io.open('remembered_ids.yaml', 'r', encoding='utf8') as infile:
                saved_data = yaml.safe_load(infile)
                return saved_data
        else:
            return []


    def remove_thumbnail_widget(self, widget):
        self.main_box.gridLayout.removeWidget(widget)
        self.thumbnail_widgets.remove(widget)
        widget.deleteLater()

        self.space_out_thumbnails()
        self.update_thumbnail_count_labels()

    def delete_all_thumbs(self):
        if len(self.thumbnail_widgets) == 0:
            return
        for widget in self.thumbnail_widgets:
            self.main_box.gridLayout.removeWidget(widget)
            widget.deleteLater()

        self.thumbnail_widgets = []

        self.space_out_thumbnails()
        self.update_thumbnail_count_labels()

    def select_file_for_thumbnails(self):
        selected_files = QFileDialog.getOpenFileNames(self,"Choose images to load",str(config.last_used_directory),config.allowed_file_types)[0]

        if not selected_files:
            print("No files were selected")
        else:
            print(Path(selected_files[0]).parent)
            config.last_used_directory = Path(selected_files[0]).parent

            with ThreadPoolExecutor() as executor:  # This was a waste of time to add...
                futures = []

                for file in selected_files:
                    if Path(file).suffix in config.readable_extensions:
                        try:
                            with Image.open(file) as open_image:
                                if open_image.size == (128, 64):
                                    print(f"found thumbnail at: {file}")
                                    futures.append(executor.submit(self.infer_thumbnail_id, file))
                        except:
                            print("Skipping invalid file")
                            continue

            results = [future.result() for future in futures]
            for widget in results:
                self.add_thumbnail(widget[0][0], widget[0][1])

            self.space_out_thumbnails()
            self.update_thumbnail_count_labels()

    def scan_folder_for_thumbnails(self):
        #TODO Change it to select specific files.

        selected_folder = QFileDialog.getExistingDirectory(self, "Choose folder containing thumbnails", str(config.last_used_directory))

        if selected_folder == "":
            print("Folder wasn't selected")
        else:
            print(selected_folder)
            config.last_used_directory = Path(selected_folder)

            with ThreadPoolExecutor() as executor:  # This was a waste of time to add...
                futures = []

                if self.main_box.search_subfolders_checkbox.checkState() == Qt.CheckState.Checked:
                    for file in Path(selected_folder).rglob('*'):
                        if Path(file).suffix in config.readable_extensions:
                            try:
                                with Image.open(file) as open_image:
                                    if open_image.size == (128, 64):
                                        print(f"found thumbnail at: {file}")
                                        futures.append(executor.submit(self.infer_thumbnail_id, file))
                            except PIL.UnidentifiedImageError:
                                print("Skipping invalid file")
                                continue
                else:
                    for file in Path(selected_folder).iterdir():
                        if Path(file).suffix in config.readable_extensions:
                            try:
                                with Image.open(file) as open_image:
                                    if open_image.size == (128, 64):
                                        print(f"found thumbnail at: {file}")
                                        futures.append(executor.submit(self.infer_thumbnail_id, file))
                            except PIL.UnidentifiedImageError:
                                print("Skipping invalid file")
                                continue

            results = [future.result() for future in futures]
            for widget in results:
                self.add_thumbnail(widget[0][0],widget[0][1])


            self.space_out_thumbnails()
            self.update_thumbnail_count_labels()

    def create_thumbnail_farc(self):
        mod_name = self.main_box.mod_name_lineedit.get_filtered_text()
        if mod_name == "":
            show_message_box("Error", "You need to specify mod name!")
        else:
            all_thumb_data = []
            for thumb_widget in self.thumbnail_widgets:
                thumb_data = []
                image_path = thumb_widget.image_path
                ids = []

                for id_list in thumb_widget.id_field_list:
                    ids.append(int(id_list.ui.song_id_spinbox.value()))

                thumb_data.append(ids)
                thumb_data.append(image_path)
                all_thumb_data.append(thumb_data)

            thumb_unique_count = 0
            for _ in all_thumb_data:
                thumb_unique_count = thumb_unique_count + 1

            texture_size = self.calculate_texture_grid(thumb_unique_count)

            if texture_size == (0,0):
                return

            thumbnail_texture = Image.new('RGBA', texture_size)
            x=2
            y=2
            thumb = 0
            thumbnail_positions = []

            for thumb_data in all_thumb_data:
            #[id,id...],image
                thumb= thumb + 1
                thumbnail_texture.alpha_composite(Image.open(thumb_data[1]),(x,y))

                for thumb_id in thumb_data[0]:
                    thumbnail_positions.append([pad_number(thumb_id), (x, y)])

                if thumb == 7:
                    x = 2
                    y = y + 64 + 2
                    thumb = 0
                else:
                    x = x + 128 + 2

            for data in thumbnail_positions:
                print(data)

            chosen_dir = QFileDialog.getExistingDirectory(self, "Choose folder to save farc file to", str(config.last_used_directory))

            if chosen_dir == "":
                print("Folder wasn't chosen")
            else:
                config.last_used_directory = Path(chosen_dir)
                self.save_pack_name()
                thumbnail_texture.save(str(config.script_directory) + "/Images/Thumbnail Texture.png","png")


                FarcCreator.create_thumbnail_farc(thumbnail_positions,str(config.script_directory) + "/Images/Thumbnail Texture.png",chosen_dir,mod_name)

                #Remember ID's used for images
                remember_data = []
                for thumb_widget in self.thumbnail_widgets:
                    image = str(thumb_widget.image_path)
                    ids = []
                    for id_field in thumb_widget.id_field_list:
                        ids.append(int(id_field.ui.song_id_spinbox.value()))
                    remember_data.append([image,ids])

                if Path('remembered_ids.yaml').exists():
                    with io.open('remembered_ids.yaml', 'r' , encoding='utf8') as infile:
                        saved_data = yaml.safe_load(infile)

                        saved_paths =  {entry[0] for entry in saved_data}
                        current_paths = {entry[0] for entry in remember_data}

                        common_paths = saved_paths & current_paths
                        untouched_saved_paths = saved_paths - common_paths

                        new_data = []

                        #Write new data for common paths and new ones
                        #Append unchanged data
                        #dump YAML

                        for entry in remember_data:
                            new_data.append(entry)

                        for entry in saved_data:
                            if entry[0] in untouched_saved_paths:
                                new_data.append(entry)

                    with io.open('remembered_ids.yaml', 'w', encoding='utf8') as outfile:
                        yaml.dump(new_data, outfile, default_flow_style=False, allow_unicode=True)

                    self.known_ids = self.read_saved_ids()

                else:
                   with io.open('remembered_ids.yaml', 'w', encoding='utf8') as outfile:
                       yaml.dump(remember_data, outfile, default_flow_style=False, allow_unicode=True)

                self.known_ids = self.read_saved_ids()

    def next_power_of_two(self,n):
        if n <= 0:
            return 1
        p = 1
        while p < n:
            p *= 2
        return p

    def calculate_texture_grid(self,thumb_amount):
        if thumb_amount <= 0:
            return 0, 0

        if thumb_amount == 1:
            tex_width = 256
            tex_height = 256
            return tex_width,tex_height
        elif thumb_amount <= 3:
            tex_width = 512
            tex_height = 256
            return tex_width, tex_height
        else:
            tex_width = 1024

            rows = math.ceil(thumb_amount / 7) # there will be 7 columns

            total_height = rows * 66 # Height of a thumbnail plus 2 pixels of a gap
            tex_height = self.next_power_of_two(total_height)
            area = (tex_width , tex_height)
        return area

    def save_pack_name(self):

        if Path('remembered_names.yaml').exists():
            with io.open('remembered_names.yaml', 'r' , encoding='utf8') as infile:
                remember_data = yaml.safe_load(infile)
                if self.main_box.mod_name_lineedit.combo_box.currentText() not in remember_data:
                    remember_data.append(self.main_box.mod_name_lineedit.combo_box.currentText())

                    with io.open('remembered_names.yaml' , 'w', encoding='utf8') as outfile:
                        yaml.dump(remember_data, outfile, default_flow_style=False, allow_unicode=True)


        else:
            remember_data = []
            for i in range(self.main_box.mod_name_lineedit.combo_box.count()):
                remember_data.append(self.main_box.mod_name_lineedit.combo_box.itemText(i))

            if self.main_box.mod_name_lineedit.combo_box.currentText() != "":
                remember_data.append(self.main_box.mod_name_lineedit.combo_box.currentText())

            with io.open('remembered_names.yaml', 'w', encoding='utf8') as outfile:
                yaml.dump(remember_data, outfile, default_flow_style=False, allow_unicode=True)

        for i in range(self.main_box.mod_name_lineedit.combo_box.count()):
            self.main_box.mod_name_lineedit.combo_box.removeItem(i)
        self.main_box.mod_name_lineedit.combo_box.addItems(remember_data)

    def fill_combobox_suggestions(self):
        if Path('remembered_names.yaml').exists():
            with io.open('remembered_names.yaml', 'r' , encoding='utf8') as infile:
                remember_data = yaml.safe_load(infile)
                self.main_box.mod_name_lineedit.combo_box.addItems(remember_data)

    def delete_selected_name(self):
        name = self.main_box.mod_name_lineedit.combo_box.currentText()
        if name == "":
            return

        edited_file = False

        if Path('remembered_names.yaml').exists():
            with io.open('remembered_names.yaml', 'r', encoding='utf8') as infile:
                remember_data = yaml.safe_load(infile)

                if name in remember_data:
                    remember_data.remove(name)
                    edited_file = True

            if edited_file:
                with io.open('remembered_names.yaml', 'w', encoding='utf8') as outfile:
                    yaml.dump(remember_data, outfile, default_flow_style=False, allow_unicode=True)



        self.main_box.mod_name_lineedit.combo_box.removeItem(self.main_box.mod_name_lineedit.combo_box.currentIndex())
        self.main_box.mod_name_lineedit.label.setText("")


###################################################################################################

def check_for_files():
    missing_files = []
    required_files = [
        config.script_directory / 'Images/Dummy/Thumbnail-Maskv2.png',
        config.script_directory / 'Images/Dummy/Thumbnail-Maskv3.png',
        config.script_directory / 'Images/Dummy/SONG_BG_DUMMY.png',
        config.script_directory / 'Images/Dummy/SONG_JK_DUMMY.png',
        config.script_directory / 'Images/Dummy/SONG_LOGO_DUMMY.png',
        config.script_directory / 'Images/Dummy/SONG_JK_THUMBNAIL_DUMMY.png',
        config.script_directory / 'Images/MM UI - Song Select/Backdrop.png',
        config.script_directory / 'Images/MM UI - Song Select/Song Selector.png',
        config.script_directory / 'Images/MM UI - Song Select/Middle Layer.png',
        config.script_directory / 'Images/MM UI - Song Select/Top Layer.png',
        config.script_directory / 'Images/MM UI - Song Select/Top Layer - New Classics.png',
        config.script_directory / 'Images/MM UI - Results Screen/Middle Layer.png',
        config.script_directory / 'Images/MM UI - Results Screen/Top Layer.png',
        config.script_directory / 'Images/MM UI - Results Screen/Top Layer - New Classics.png',
        config.script_directory / 'Images/FT UI - Song Select/Base.png',
        config.script_directory / 'Images/FT UI - Song Select/Middle Layer.png',
        config.script_directory / 'Images/FT UI - Song Select/Top Layer.png',
        config.script_directory / 'Images/FT UI - Song Select/Top Layer - New Classics.png',
        config.script_directory / 'Images/FT UI - Results Screen/Base.png',
        config.script_directory / 'Images/FT UI - Results Screen/Middle Layer.png',
        config.script_directory / 'Images/FT UI - Results Screen/Top Layer.png',
        config.script_directory / 'Images/FT UI - Results Screen/Top Layer - New Classics.png'
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

class MainWindow(QMainWindow):



    def __init__(self):
        super(MainWindow, self).__init__()
        self.main_box = Ui_MainWindow()
        self.main_box.setupUi(self)
        color = self.palette().color(QPalette.ColorRole.Window)
        self.main_box.graphics_scene_view.setBackgroundBrush(color)
        self.main_box.graphics_scene_view1.setBackgroundBrush(color)
        self.main_box.graphics_scene_view2.setBackgroundBrush(color)
        self.main_box.graphics_scene_view3.setBackgroundBrush(color)

        check_for_files()

        #Prepare new window
        self.thumbnail_creator = ThumbnailWindow()

        #Start watching for file updates of loaded files
        self.watcher = QFileSystemWatcher()
        self.watcher.fileChanged.connect(self.watcher_file_modified_action)

        self.main_box.export_background_jacket_button.clicked.connect(self.export_background_jacket_button_callback)
        self.main_box.export_thumbnail_button.clicked.connect(self.export_thumbnail_button_callback)
        self.main_box.export_logo_button.clicked.connect(self.export_logo_button_callback)

        self.main_box.copy_to_clipboard_button.clicked.connect(lambda: self.generate_preview(OutputTarget.CLIPBOARD))
        self.main_box.open_preview_button.clicked.connect(lambda: self.generate_preview(OutputTarget.IMAGE_VIEWER))
        self.main_box.generate_spr_db_button.clicked.connect(self.generate_spr_db_button_callback)

        self.main_box.farc_create_thumbnail_button.clicked.connect(lambda: self.thumbnail_creator.show())
        self.main_box.farc_export_button.clicked.connect(self.export_background_jacket_logo_farc_button_callback)
        self.main_box.flip_horizontal_button.clicked.connect(lambda: self.flip_current_sprite(Qt.Orientation.Horizontal))
        self.main_box.flip_vertical_button.clicked.connect(lambda: self.flip_current_sprite(Qt.Orientation.Vertical))



        self.main_box.current_sprite_combobox.currentIndexChanged.connect(lambda: self.current_sprite_tab_switcher(self.main_box.current_sprite_combobox.currentIndex()))

        #Connect checkboxes with their functions
        self.main_box.has_logo_checkbox.checkStateChanged.connect(self.has_logo_checkbox_callback)
        self.main_box.new_classics_checkbox.checkStateChanged.connect(self.toggle_new_classics)

        self.display_scenes()

        #Make sure that tab matches options shown on start
        self.current_sprite_tab_switcher(self.main_box.current_sprite_combobox.currentIndex())




    def resizeEvent(self,event):
        #Todo allow resizing by grabbing top/bottom edge too

        # Force 2:1 aspect ratio
        new_width = self.size().width()
        new_height = int(new_width / 2)
        size = QSize(new_width,new_height)
        self.resize(size)

    def current_sprite_tab_switcher(self,tab):
        self.main_box.sprite_controls.setCurrentIndex(tab)

        self.main_box.load_image_button.clicked.disconnect()

        sprite = self.main_box.current_sprite_combobox.currentText()
        self.main_box.load_image_button.clicked.connect(lambda:self.load_new_sprite_image(sprite))
        self.main_box.load_image_button.setText(f"Load {sprite} Image")

        match sprite:
            case "Background":
                self.main_box.load_image_button.setEnabled(self.C_Sprites.background.controls_enabled)
                self.main_box.flip_vertical_button.setEnabled(self.C_Sprites.background.controls_enabled)
                self.main_box.flip_horizontal_button.setEnabled(self.C_Sprites.background.controls_enabled)
            case "Jacket":
                self.main_box.load_image_button.setEnabled(self.C_Sprites.jacket.controls_enabled)
                self.main_box.flip_vertical_button.setEnabled(self.C_Sprites.jacket.controls_enabled)
                self.main_box.flip_horizontal_button.setEnabled(self.C_Sprites.jacket.controls_enabled)
            case "Logo":
                self.main_box.load_image_button.setEnabled(self.C_Sprites.logo.controls_enabled)
                self.main_box.flip_vertical_button.setEnabled(self.C_Sprites.logo.controls_enabled)
                self.main_box.flip_horizontal_button.setEnabled(self.C_Sprites.logo.controls_enabled)
            case "Thumbnail":
                self.main_box.load_image_button.setEnabled(self.C_Sprites.thumbnail.controls_enabled)
                self.main_box.flip_vertical_button.setEnabled(self.C_Sprites.thumbnail.controls_enabled)
                self.main_box.flip_horizontal_button.setEnabled(self.C_Sprites.thumbnail.controls_enabled)

    def flip_current_sprite(self,flip_type):
        current_sprite = self.main_box.current_sprite_combobox.currentText()
        match current_sprite:
            case "Background":
                self.C_Sprites.background.toggle_flip(flip_type)
            case "Jacket":
                self.C_Sprites.jacket.toggle_flip(flip_type)
            case "Logo":
                self.C_Sprites.logo.toggle_flip(flip_type)
            case "Thumbnail":
                self.C_Sprites.thumbnail.toggle_flip(flip_type)

    def display_scenes(self):
        self.C_Sprites = QControllableSprites()
        self.P_Scenes = QPreviewScenes(self.C_Sprites)

        self.C_Sprites.thumbnail.add_edit_controls_to(self.main_box.verticalLayout_12)
        self.C_Sprites.logo.add_edit_controls_to(self.main_box.verticalLayout_11)
        self.C_Sprites.jacket.add_edit_controls_to(self.main_box.verticalLayout_10)
        self.C_Sprites.background.add_edit_controls_to(self.main_box.verticalLayout_8)

        self.main_box.graphics_scene_view1.setScene(self.P_Scenes.MM_SongSelect)
        self.main_box.graphics_scene_view3.setScene(self.P_Scenes.FT_SongSelect)
        self.main_box.graphics_scene_view.setScene(self.P_Scenes.MM_Result)
        self.main_box.graphics_scene_view2.setScene(self.P_Scenes.FT_Result)


    def generate_preview(self,target:OutputTarget):
        #Update sprites so they use HQ versions
        self.C_Sprites.jacket.update_sprite(hq_output=True)
        self.C_Sprites.background.update_sprite(hq_output=True)
        self.C_Sprites.thumbnail.update_sprite(hq_output=True)
        self.C_Sprites.logo.update_sprite(hq_output=True)

        preview = QImage(QSize(3840,2160),QImage.Format.Format_ARGB32)
        painter = QPainter(preview)
        self.P_Scenes.MM_SongSelect.render(painter,target=QRectF(0,0,1920,1080))
        self.P_Scenes.FT_SongSelect.render(painter, target=QRectF(1920, 0, 1920, 1080))
        self.P_Scenes.MM_Result.render(painter, target=QRectF(0, 1080, 1920, 1080))
        self.P_Scenes.FT_Result.render(painter, target=QRectF(1920, 1080, 1920, 1080))
        painter.end()

        match target:
            case OutputTarget.CLIPBOARD:
                clipboard = QGuiApplication.clipboard()
                clipboard.setImage(preview)

            case OutputTarget.IMAGE_VIEWER:
                temp_dir = QStandardPaths.writableLocation(QStandardPaths.TempLocation)
                temp_file = os.path.join(temp_dir, "qt_image.png")

                if preview.save(temp_file, "JPEG"):
                    url = QUrl.fromLocalFile(temp_file)
                    QDesktopServices.openUrl(url)

    def watcher_file_modified_action(self,path):
        sleep(2)
        keep_watching_path = False

        for sprite in self.C_Sprites.list:
            if path == sprite.location:
                print(f"{sprite.type.value} image was changed")
                if sprite.load_new_image(path,fallback=True) == "Updated":
                     keep_watching_path = True

        if keep_watching_path:
            self.watcher.removePath(path)
            self.watcher.addPath(path)
        else:
            self.watcher.removePath(path)

    def has_logo_checkbox_callback(self):
        if self.main_box.has_logo_checkbox.checkState() == Qt.CheckState.Checked:
            state = True
            self.main_box.export_logo_button.setToolTip("")
        else:
            state = False
            self.main_box.export_logo_button.setToolTip("Logo is disabled.")

        self.C_Sprites.logo.toggle_visibility(state)
        self.main_box.export_logo_button.setEnabled(state)
        if self.main_box.current_sprite_combobox.currentText() == "Logo":
            self.main_box.load_image_button.setEnabled(state)
            self.main_box.flip_vertical_button.setEnabled(state)
            self.main_box.flip_horizontal_button.setEnabled(state)
    def toggle_new_classics(self):
        if self.main_box.new_classics_checkbox.checkState() == Qt.CheckState.Checked:
            state = True
        else:
            state = False
        self.P_Scenes.MM_SongSelect.toggle_new_classics(state)
        self.P_Scenes.FT_SongSelect.toggle_new_classics(state)
        self.P_Scenes.MM_Result.toggle_new_classics(state)
        self.P_Scenes.FT_Result.toggle_new_classics(state)



    def load_new_sprite_image(self,sprite):
        sprite_object = None
        match sprite:
            case "Background":
                sprite_object = self.C_Sprites.background
            case "Jacket":
                sprite_object = self.C_Sprites.jacket
            case "Thumbnail":
                sprite_object = self.C_Sprites.thumbnail
            case "Logo":
                sprite_object = self.C_Sprites.logo

        image_location = QFileDialog.getOpenFileName(self,
                                                 f"Open {sprite_object.type.value} image",
                                                 str(config.last_used_directory),
                                                 config.allowed_file_types)[0]
        if image_location == "":
            print("User didn't select image")
        else:
            config.last_used_directory = Path(image_location).parent
            if sprite_object.load_new_image(image_location) == "Updated":
                self.watcher.addPath(image_location)

    def create_background_jacket_texture(self):
        self.C_Sprites.background.update_sprite(hq_output=True)
        self.C_Sprites.jacket.update_sprite(hq_output=True)

        background_jacket_texture = QImage(QSize(2048, 1024),QImage.Format.Format_ARGB32)
        background_jacket_texture.fill(Qt.GlobalColor.transparent)
        painter = QPainter(background_jacket_texture)
        painter.setRenderHint(QPainter.RenderHint.LosslessImageRendering)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.VerticalSubpixelPositioning)

        painter.drawPixmap(0,0,self.C_Sprites.background.pixmap().scaled(1282,722))
        painter.drawPixmap(1,1,self.C_Sprites.background.pixmap())
        painter.drawPixmap(1286, 2,self.C_Sprites.jacket.pixmap())
        painter.end()

        return background_jacket_texture
    def create_logo_texture(self) -> QImage:
        self.C_Sprites.logo.update_sprite(hq_output=True)

        logo = self.C_Sprites.logo.pixmap()
        logo_texture = QImage(QSize(1024, 512), QImage.Format.Format_ARGB32)
        logo_texture.fill(Qt.GlobalColor.transparent)
        painter = QPainter(logo_texture)
        painter.setRenderHint(QPainter.RenderHint.LosslessImageRendering)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.VerticalSubpixelPositioning)
        painter.drawPixmap(2,2,logo)
        painter.end()
        return logo_texture
    def create_thumbnail_texture(self) -> QImage:
        self.C_Sprites.thumbnail.update_sprite(hq_output=True)

        thumbnail = QPixmap(self.C_Sprites.thumbnail.pixmap_no_mask)
        thumbnail_texture = QImage(QSize(128, 64), QImage.Format.Format_RGBA8888)
        thumbnail_texture.fill(Qt.GlobalColor.transparent)
        painter = QPainter(thumbnail_texture)
        painter.setRenderHint(QPainter.RenderHint.LosslessImageRendering)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.VerticalSubpixelPositioning)
        painter.drawPixmap(0, 0, thumbnail)
        painter.end()
        return thumbnail_texture

    def export_background_jacket_button_callback(self):
        save_location = QFileDialog.getSaveFileName(self, "Save File",str(config.last_used_directory)+"/Background Texture.png","Images (*.png)")[0]

        if save_location == "":
            print("Directory wasn't chosen")
        else:
            config.last_used_directory = Path(save_location).parent
            background_jacket_texture = self.create_background_jacket_texture()
            background_jacket_texture.save(save_location,"png")
    def export_thumbnail_button_callback(self):
        save_location = QFileDialog.getSaveFileName(self, "Save File", str(config.last_used_directory) + "/Thumbnail Texture.png", "Images (*.png)")[0]
        if save_location == "":
            print("Directory wasn't chosen")
        else:
            config.last_used_directory = Path(save_location)
            thumbnail_texture = self.create_thumbnail_texture()
            mask = str(Path.cwd() / "Images/Dummy/Thumbnail-Maskv3.png")
            self.export_qimage_with_mask(thumbnail_texture,mask,save_location)
    def export_logo_button_callback(self):
        filename, _ = QFileDialog.getSaveFileName(
            None,
            "Save Image",
            str(config.last_used_directory) + "/Logo Texture.png",
            "PNG Files (*.png)"
        )
        if filename == "":
            print("Directory wasn't chosen")
        else:
            config.last_used_directory = Path(filename).parent
            logo_texture = self.create_logo_texture()
            logo_texture.save(filename, "png")
    def export_background_jacket_logo_farc_button_callback(self):
        output_location = QFileDialog.getExistingDirectory(self, "Choose folder to save farc file to", str(config.last_used_directory))

        if output_location == "":
            print("Directory wasn't chosen")
        else:
            config.last_used_directory = Path(output_location)

            QImage(self.create_background_jacket_texture()).save(str(config.script_directory / 'Images/Background Texture.png'))
            QImage(self.create_logo_texture()).save(str(config.script_directory / 'Images/Logo Texture.png'))
            song_id = pad_number(int(self.main_box.farc_song_id_spinbox.value()))

            output_location = output_location
            if self.main_box.has_logo_checkbox.checkState() == Qt.CheckState.Checked:
                logo_state = True
            else:
                logo_state = False
            FarcCreator.create_jk_bg_logo_farc(song_id, str(config.script_directory / 'Images/Background Texture.png'), str(config.script_directory / 'Images/Logo Texture.png'), output_location, logo_state)

    def export_qimage_with_mask(self,qimage:QImage, mask_path:str, output_path:str):
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            if not qimage.save(temp_path):
                raise ValueError("Failed to save QImage to temporary file")

            with WImage(filename=temp_path) as img:
                with WImage(filename=mask_path) as mask_img:
                    if img.size != mask_img.size:
                        mask_img.resize(img.width, img.height)

                    img.composite(mask_img, operator='copy_alpha')

                    img.save(filename=output_path)

        except Exception as e:
            print(f"Error during image processing: {str(e)}")
            raise
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def generate_spr_db_button_callback(self):
        spr_path = QFileDialog.getExistingDirectory(self,"Choose 2d folder to generate spr_db for",str(config.last_used_directory))
        #TODO add warning about using multiple new thumbnail files in single mod. Should prevent user from generating sprite database until this gets fixed

        if spr_path == "":
            print("Folder wasn't chosen")
        else:
            spr_db = Manager()
            farc_list = []
            config.last_used_directory = Path(spr_path)
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
                    elif farc_file.name[:14] == "spr_sel_pvtmb_":
                        has_new_tmb_farc = True
                if has_new_tmb_farc:
                    if has_old_tmb_farc:
                        farc_list.remove(Path(spr_path + "/spr_sel_pvtmb.farc"))
                        show_message_box("Warning", "You have included both new and old thumbnail farcs in your mod! Generating spr_db for old combined thumbnail farc was skipped."
                                                    "\n"
                                                    "\nPlease remove 'spr_sel_pvtmb.farc' from your mod to avoid issues.")
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
    FarcCreator = FarcCreator()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    main_window = MainWindow()
    main_window.show()
    app.exec()