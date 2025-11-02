import io
import time
from pathlib import Path, PurePath
import sys , os
import math
import re
import string
import yaml
from time import sleep
from enum import Enum, auto

import PIL.ImageShow
from PySide6.QtCore import Qt, Slot, QFileSystemWatcher, QSize, Signal, QRect, QRectF, QPoint
from PySide6.QtGui import QPixmap, QPalette, QColor, QBrush, QImage, QPainter, QBitmap
from PySide6.QtWidgets import QApplication, QMessageBox, QMainWindow, QWidget, QFrame, QFileDialog, QLabel, QSpacerItem, QSizePolicy, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QGraphicsOpacityEffect
from PIL import Image,ImageShow,ImageStat
from PIL.ImageShow import Viewer

from concurrent.futures import ThreadPoolExecutor

from copykitten import copy_image
from decimal import Decimal, ROUND_HALF_UP

from superqt.utils import qthrottled

from SceneComposer import SceneComposer, State, SpriteType, Scene, SpriteSetting, QThumbnail, QSpriteBase, QMMSongSelectScene
from FarcCreator import FarcCreator
from auto_creat_mod_spr_db import Manager, add_farc_to_Manager, read_farc

from ui_ThumbnailTextureCreator import Ui_ThumbnailTextureCreator
from ui_ThumbnailWidget import Ui_ThumbnailWidget
from ui_ThumbnailIDField import  Ui_ThumbnailIDField
from ui_SpriteHelper import Ui_MainWindow

from widgets import Stylesheet,EditableDoubleLabel

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
        #print("called add")
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
        print("remove")
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
                #print(f"inferring {entry[1]} from YAML")
                break

        if inferred_id_list == []:
            if Path(image_path).stem.isdigit() and len(Path(image_path).stem) >= 3:
                id_list = [Path(image_path).stem]
                inferred_id_list.append([image_path,id_list])
                #print(f"inferring {id_list} from file name")
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

        if selected_files == []:
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
        #TODO Needs to skip over problematic files.
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
            for thumb in all_thumb_data:
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
            #print(thumbnail_positions[0][0])
            #TODO fix sorting. Needs to sort by id that's now a string so it shits itself
            #thumbnail_positions.sort()

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
            return (0, 0)

        if thumb_amount == 1:
            tex_width = 256
            tex_height = 256
            return (tex_width,tex_height)
        elif thumb_amount <= 3:
            tex_width = 512
            tex_height = 256
            return (tex_width, tex_height)
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

def texture_filtering_fix(image,opacity):
    #Very edges of the sprite should have like 40% opacity. This makes jackets appear smooth in-game.
    t_edge = Image.new(image.mode,(image.size[0],image.size[1]))
    t_edge.alpha_composite(image)
    t_edge = t_edge.resize((image.size[0]+2,image.size[1]+2))
    r,g,b,a = t_edge.split()
    a = a.point(lambda  x: opacity if x > 0 else 0) #Set 102 opacity, that is 40% from 256. For Background 100% is recommended
    t_edge = Image.merge(image.mode,(r,g,b,a))
    t_edge.alpha_composite(image,(1,1))
    return t_edge

def check_for_files():
    missing_files = []
    required_files = [
        config.script_directory / 'Images/Dummy/Thumbnail-Maskv2.png',
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

@Slot()
def draw_combined_preview_to(target):
    #TODO use pixmap.save to avoid re-rendering the scenes
    new_classics_state = main_window.main_box.new_classics_checkbox.isChecked()
    composite = Image.new('RGBA', (3840, 2160), (0, 0, 0, 0))
    composite.alpha_composite(SceneComposer.Megamix_Song_Select.compose_scene(new_classics_state))
    composite.alpha_composite(SceneComposer.Megamix_Result.compose_scene(new_classics_state),(0, 1080))
    composite.alpha_composite(SceneComposer.FutureTone_Song_Select.compose_scene(new_classics_state), (1920, 0))
    composite.alpha_composite(SceneComposer.FutureTone_Result.compose_scene(new_classics_state), (1920, 1080))

    match target:
        case OutputTarget.CLIPBOARD:
            pixels = composite.tobytes()
            copy_image(pixels, composite.width, composite.height)

        case OutputTarget.IMAGE_VIEWER:
            ImageShow.show(composite)

class MainWindow(QMainWindow):



    def __init__(self):
        super(MainWindow, self).__init__()
        self.main_box = Ui_MainWindow()
        self.main_box.setupUi(self)

        #Create dictionary that will contain all sprite controls
        self.edit_control = {}
        # TODO add all edit controls via list from SceneComposer
        self.add_edit_control(SceneComposer.Background)
        self.add_edit_control(SceneComposer.Jacket)
        self.add_edit_control(SceneComposer.Thumbnail)
        self.add_edit_control(SceneComposer.Logo)

        check_for_files()
        self.reload_images()

        #Prepare new window
        self.thumbnail_creator = ThumbnailWindow()

        #Start watching for file updates of loaded files
        self.watcher = QFileSystemWatcher()
        self.watcher.fileChanged.connect(self.watcher_file_modified_action)
        self.watcher.addPath(str(SceneComposer.Background.location))
        self.watcher.addPath(str(SceneComposer.Jacket.location))
        self.watcher.addPath(str(SceneComposer.Logo.location))
        self.watcher.addPath(str(SceneComposer.Thumbnail.location))

        #Connect buttons with their functionality
        self.main_box.load_background_button.clicked.connect(self.load_background_button_callback)
        self.main_box.load_thumbnail_button.clicked.connect(lambda: self.load_new_sprite_image(self.thumbnail))
        self.main_box.load_logo_button.clicked.connect(self.load_logo_button_callback)
        self.main_box.load_jacket_button.clicked.connect(self.load_jacket_button_callback)
        self.main_box.copy_to_clipboard_button.clicked.connect(lambda: draw_combined_preview_to(OutputTarget.CLIPBOARD))
        self.main_box.open_preview_button.clicked.connect(lambda: draw_combined_preview_to(OutputTarget.IMAGE_VIEWER))
        self.main_box.export_background_jacket_button.clicked.connect(self.export_background_jacket_button_callback)
        self.main_box.export_thumbnail_button.clicked.connect(self.export_thumbnail_button_callback)
        self.main_box.export_logo_button.clicked.connect(self.export_logo_button_callback)
        self.main_box.generate_spr_db_button.clicked.connect(self.generate_spr_db_button_callback)
        self.main_box.farc_create_thumbnail_button.clicked.connect(lambda: self.thumbnail_creator.show())
        self.main_box.farc_export_button.clicked.connect(self.export_background_jacket_logo_farc_button_callback)
        self.main_box.flip_horizontal_button.clicked.connect(lambda: self.flip_current_sprite("Horizontal"))
        self.main_box.flip_vertical_button.clicked.connect(lambda: self.flip_current_sprite("Vertical"))
        #Connect spinboxes with functions that update their sprites
        self.spinbox_editing_finished_trigger("on")
        #Allow previews to be opened in external viewer
        self.main_box.mm_song_selector_preview.clicked.connect(lambda: self.view_pixmap_external(Scene.MEGAMIX_SONG_SELECT))
        self.main_box.ft_song_selector_preview.clicked.connect(lambda: self.view_pixmap_external(Scene.FUTURE_TONE_SONG_SELECT))
        self.main_box.mm_result_preview.clicked.connect(lambda: self.view_pixmap_external(Scene.MEGAMIX_RESULT))
        self.main_box.ft_result_preview.clicked.connect(lambda: self.view_pixmap_external(Scene.FUTURE_TONE_RESULT))
        self.main_box.mm_song_selector_preview.setCursor(Qt.CursorShape.PointingHandCursor)
        self.main_box.ft_song_selector_preview.setCursor(Qt.CursorShape.PointingHandCursor)
        self.main_box.mm_result_preview.setCursor(Qt.CursorShape.PointingHandCursor)
        self.main_box.ft_result_preview.setCursor(Qt.CursorShape.PointingHandCursor)

        self.main_box.current_sprite_combobox.currentIndexChanged.connect(lambda: self.current_sprite_tab_switcher(self.main_box.current_sprite_combobox.currentIndex()))

        #Connect checkboxes with their functions
        self.main_box.has_logo_checkbox.checkStateChanged.connect(self.has_logo_checkbox_callback)
        self.main_box.new_classics_checkbox.checkStateChanged.connect(self.refresh_image_grid)

        self.current_sprite_tab_switcher(self.main_box.current_sprite_combobox.currentIndex()) # Make sure that tab matches options shown on start

        print("Initial Draw")
        self.draw_image_grid()

        self.benchmark()

    def resizeEvent(self,event):
        #Todo allow resizing by grabbing top/bottom edge too

        # Force 2:1 aspect ratio
        new_width = self.size().width()
        new_height = int(new_width / 2)
        size = QSize(new_width,new_height)
        self.resize(size)

    def current_sprite_tab_switcher(self,tab):
        self.main_box.sprite_controls.setCurrentIndex(tab)


    def view_pixmap_external(self,scene):
        #TODO use pixmap.save to not re-render scene
        new_classics_state = main_window.main_box.new_classics_checkbox.isChecked()
        match scene:
            case Scene.MEGAMIX_SONG_SELECT:
                ImageShow.show(SceneComposer.Megamix_Song_Select.compose_scene(new_classics_state))
            case Scene.FUTURE_TONE_SONG_SELECT:
                ImageShow.show(SceneComposer.FutureTone_Song_Select.compose_scene(new_classics_state))
            case Scene.MEGAMIX_RESULT:
                ImageShow.show(SceneComposer.Megamix_Result.compose_scene(new_classics_state))
            case Scene.FUTURE_TONE_RESULT:
                ImageShow.show(SceneComposer.FutureTone_Result.compose_scene(new_classics_state))

    def draw_scene(self, ui_scene):
        new_classics_state = self.main_box.new_classics_checkbox.isChecked()
        match ui_scene:
            case Scene.MEGAMIX_SONG_SELECT:
                self.main_box.mm_song_selector_preview.setPixmap(SceneComposer.Megamix_Song_Select.compose_scene(new_classics_state).toqpixmap())
            case Scene.FUTURE_TONE_SONG_SELECT:
                self.main_box.ft_song_selector_preview.setPixmap(SceneComposer.FutureTone_Song_Select.compose_scene(new_classics_state).toqpixmap())
            case Scene.MEGAMIX_RESULT:
                self.main_box.mm_result_preview.setPixmap(SceneComposer.Megamix_Result.compose_scene(new_classics_state).toqpixmap())
            case Scene.FUTURE_TONE_RESULT:
                self.main_box.ft_result_preview.setPixmap(SceneComposer.FutureTone_Result.compose_scene(new_classics_state).toqpixmap())

    def draw_image_grid(self):
        start_time = time.time()
        with ThreadPoolExecutor() as executor:
            for scene in config.scenes_to_draw:
                executor.submit(self.draw_scene,scene)
        print("--- %s seconds ---" % (time.time() - start_time))

        Jacket_state = SceneComposer.check_sprite(SpriteType.JACKET)
        Background_state = SceneComposer.check_sprite(SpriteType.BACKGROUND)

        if Jacket_state == False or Background_state == False:
            failed_check = []
            if not Jacket_state:
                print("Jacket is fucked up")
                failed_check.append("Jacket")
            else:
                print("Jacket is fine")
            if not Background_state:
                print("Background is fucked up")
                failed_check.append("Background")
            else:
                print("Background is fine")

            self.main_box.export_background_jacket_button.setEnabled(False)
            self.main_box.export_background_jacket_button.setToolTip(f"{' and '.join(failed_check)} area isn't fully filled by opaque image!")
            self.main_box.farc_export_button.setEnabled(False)
            self.main_box.farc_export_button.setToolTip(f"{' and '.join(failed_check)} area isn't fully filled by opaque image!")
        else:
            print("Jacket is fine")
            print("Background is fine")
            self.main_box.export_background_jacket_button.setEnabled(True)
            self.main_box.export_background_jacket_button.setToolTip("")
            self.main_box.farc_export_button.setEnabled(True)
            self.main_box.farc_export_button.setToolTip("")

        Thumbnail_state = SceneComposer.check_sprite(SpriteType.THUMBNAIL)

        if not Thumbnail_state:
            print("Thumbnail is fucked up")
            self.main_box.export_thumbnail_button.setEnabled(False)
            self.main_box.export_thumbnail_button.setToolTip("Thumbnail isn't fully filled by opaque image!")
        else:
            print("Thumbnail is fine")
            self.main_box.export_thumbnail_button.setEnabled(True)
            self.main_box.export_thumbnail_button.setToolTip("")

    def add_edit_control(self,sprite):
        editable_values = {}

        for setting in sprite.sprite_settings:
            parameters = setting[1]
            edit = EditableDoubleLabel(sprite=sprite,setting=setting[0], range=sprite.calculate_range(setting[0]),**parameters)
            editable_values[setting[0].value] = edit

            #TODO make it properly, not hardcode
            # match sprite:
            #     case SceneComposer.Background:
            #         self.main_box.verticalLayout_8.addWidget(edit)
            #     case SceneComposer.Jacket:
            #         self.main_box.verticalLayout_10.addWidget(edit)
            #     case SceneComposer.Thumbnail:
            #         self.main_box.verticalLayout_12.addWidget(edit)
            #     case SceneComposer.Logo:
            #         self.main_box.verticalLayout_11.addWidget(edit)


        self.edit_control[sprite.type.value] = editable_values

    @qthrottled(timeout=30)
    def jacket_value_edit_trigger(self):
        for control in self.edit_control[SpriteType.JACKET]:
            self.edit_control[SpriteType.JACKET][control].block_drawing = True

        SceneComposer.Jacket.post_process(self.edit_control[SpriteType.JACKET][SpriteSetting.HORIZONTAL_OFFSET].value,
                                          self.edit_control[SpriteType.JACKET][SpriteSetting.VERTICAL_OFFSET].value,
                                          self.edit_control[SpriteType.JACKET][SpriteSetting.ROTATION].value,
                                          self.edit_control[SpriteType.JACKET][SpriteSetting.ZOOM].value)

        self.edit_control[SpriteType.JACKET][SpriteSetting.HORIZONTAL_OFFSET].set_range(SceneComposer.Jacket.calculate_range(SpriteSetting.HORIZONTAL_OFFSET))
        self.edit_control[SpriteType.JACKET][SpriteSetting.VERTICAL_OFFSET].set_range(SceneComposer.Jacket.calculate_range(SpriteSetting.VERTICAL_OFFSET))

        SceneComposer.Jacket.post_process(self.edit_control[SpriteType.JACKET][SpriteSetting.HORIZONTAL_OFFSET].value,
                                          self.edit_control[SpriteType.JACKET][SpriteSetting.VERTICAL_OFFSET].value,
                                          self.edit_control[SpriteType.JACKET][SpriteSetting.ROTATION].value,
                                          self.edit_control[SpriteType.JACKET][SpriteSetting.ZOOM].value)

        for control in self.edit_control[SpriteType.JACKET]:
            self.edit_control[SpriteType.JACKET][control].block_drawing = False
        print("Jacket Triggered draw")
        self.draw_image_grid()
    #@qthrottled(timeout=30)
    def logo_value_edit_trigger(self):
        #self.logo.setRotation(self.edit_control[SpriteType.LOGO][SpriteSetting.ROTATION].value)
        # for control in self.edit_control[SpriteType.LOGO]:
        #     self.edit_control[SpriteType.LOGO][control].block_drawing = True
        #
        # SceneComposer.Logo.post_process(self.main_box.has_logo_checkbox.checkState(),
        #                                 self.edit_control[SpriteType.LOGO][SpriteSetting.HORIZONTAL_OFFSET].value,
        #                                 self.edit_control[SpriteType.LOGO][SpriteSetting.VERTICAL_OFFSET].value,
        #                                 self.edit_control[SpriteType.LOGO][SpriteSetting.ROTATION].value,
        #                                 self.edit_control[SpriteType.LOGO][SpriteSetting.ZOOM].value)
        #
        # self.edit_control[SpriteType.LOGO][SpriteSetting.HORIZONTAL_OFFSET].set_range(SceneComposer.Logo.calculate_range(SpriteSetting.HORIZONTAL_OFFSET))
        # self.edit_control[SpriteType.LOGO][SpriteSetting.VERTICAL_OFFSET].set_range(SceneComposer.Logo.calculate_range(SpriteSetting.VERTICAL_OFFSET))
        #
        # SceneComposer.Logo.post_process(self.main_box.has_logo_checkbox.checkState(),
        #                                 self.edit_control[SpriteType.LOGO][SpriteSetting.HORIZONTAL_OFFSET].value,
        #                                 self.edit_control[SpriteType.LOGO][SpriteSetting.VERTICAL_OFFSET].value,
        #                                 self.edit_control[SpriteType.LOGO][SpriteSetting.ROTATION].value,
        #                                 self.edit_control[SpriteType.LOGO][SpriteSetting.ZOOM].value)
        #
        # for control in self.edit_control[SpriteType.LOGO]:
        #     self.edit_control[SpriteType.LOGO][control].block_drawing = False
        # print("Logo Trigered draw")
        # self.draw_image_grid()
        pass
    @qthrottled(timeout=30)
    def background_value_edit_trigger(self):
        for control in self.edit_control[SpriteType.BACKGROUND]:
            self.edit_control[SpriteType.BACKGROUND][control].block_drawing = True

        SceneComposer.Background.post_process(self.edit_control[SpriteType.BACKGROUND][SpriteSetting.HORIZONTAL_OFFSET].value,
                                              self.edit_control[SpriteType.BACKGROUND][SpriteSetting.VERTICAL_OFFSET].value,
                                              self.edit_control[SpriteType.BACKGROUND][SpriteSetting.ROTATION].value,
                                              self.edit_control[SpriteType.BACKGROUND][SpriteSetting.ZOOM].value)

        self.edit_control[SpriteType.BACKGROUND][SpriteSetting.HORIZONTAL_OFFSET].set_range(SceneComposer.Background.calculate_range(SpriteSetting.HORIZONTAL_OFFSET))
        self.edit_control[SpriteType.BACKGROUND][SpriteSetting.VERTICAL_OFFSET].set_range(SceneComposer.Background.calculate_range(SpriteSetting.VERTICAL_OFFSET))

        SceneComposer.Background.post_process(self.edit_control[SpriteType.BACKGROUND][SpriteSetting.HORIZONTAL_OFFSET].value,
                                              self.edit_control[SpriteType.BACKGROUND][SpriteSetting.VERTICAL_OFFSET].value,
                                              self.edit_control[SpriteType.BACKGROUND][SpriteSetting.ROTATION].value,
                                              self.edit_control[SpriteType.BACKGROUND][SpriteSetting.ZOOM].value)

        for control in self.edit_control[SpriteType.BACKGROUND]:
            self.edit_control[SpriteType.BACKGROUND][control].block_drawing = False
        print("Background Triggered draw")
        self.draw_image_grid()
    @qthrottled(timeout=30)
    def thumbnail_value_edit_trigger(self):
        pass
        #self.thumbnail.setRotation(self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.ROTATION].value)
        #self.clipped_thumb.setPixmap(self.create_masked_scene_portion(self.thumbnail_scene, QRectF(0, 0, 128, 64), self.thumbnail_mask))
        # for control in self.edit_control[SpriteType.THUMBNAIL]:
        #     self.edit_control[SpriteType.THUMBNAIL][control].block_drawing = True
        #
        # SceneComposer.Thumbnail.post_process(self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.HORIZONTAL_OFFSET].value,
        #                                      self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.VERTICAL_OFFSET].value,
        #                                      self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.ROTATION].value,
        #                                      self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.ZOOM].value)
        #
        # self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.HORIZONTAL_OFFSET].set_range(SceneComposer.Thumbnail.calculate_range(SpriteSetting.HORIZONTAL_OFFSET))
        # self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.VERTICAL_OFFSET].set_range(SceneComposer.Thumbnail.calculate_range(SpriteSetting.VERTICAL_OFFSET))
        #
        # SceneComposer.Thumbnail.post_process(self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.HORIZONTAL_OFFSET].value,
        #                                      self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.VERTICAL_OFFSET].value,
        #                                      self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.ROTATION].value,
        #                                      self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.ZOOM].value)
        #
        # for control in self.edit_control[SpriteType.THUMBNAIL]:
        #     self.edit_control[SpriteType.THUMBNAIL][control].block_drawing = False
        # print("Thumbnail triggered draw")
        # self.draw_image_grid()

    def flip_current_sprite(self,flip_type):
        current_sprite = self.main_box.current_sprite_combobox.currentText()
        match current_sprite:
            case "Background":
                match flip_type:
                    case "Horizontal":
                        SceneComposer.Background.flipped_h = not SceneComposer.Background.flipped_h
                    case "Vertical":
                        SceneComposer.Background.flipped_v = not SceneComposer.Background.flipped_v
            case "Jacket":
                match flip_type:
                    case "Horizontal":
                        SceneComposer.Jacket.flipped_h = not SceneComposer.Jacket.flipped_h
                    case "Vertical":
                        SceneComposer.Jacket.flipped_v = not SceneComposer.Jacket.flipped_v
            case "Logo":
                match flip_type:
                    case "Horizontal":
                        SceneComposer.Logo.flipped_h = not SceneComposer.Logo.flipped_h
                    case "Vertical":
                        SceneComposer.Logo.flipped_v = not SceneComposer.Logo.flipped_v
            case "Thumbnail":
                match flip_type:
                    case "Horizontal":
                        self.thumbnail.flipped_h = not self.thumbnail.flipped_h
                    case "Vertical":
                        self.thumbnail.flipped_v = not self.thumbnail.flipped_v
        self.reload_images()
        self.draw_image_grid()

    def benchmark(self):
        self.MM_SongSelect = QMMSongSelectScene()
        self.MM_SongSelect.thumbnail_1.add_edit_controls_to(self.main_box.verticalLayout_12)



        self.main_box.graphics_scene_view.setScene(self.MM_SongSelect.scene)
        #self.thumbnail.setPixmap(Image.open(Path.cwd() / 'Images/Dummy/Jacket.png').convert('RGBA').toqpixmap())

    def reload_images(self):
        SceneComposer.Background.post_process(self.edit_control[SpriteType.BACKGROUND][SpriteSetting.HORIZONTAL_OFFSET].value,
                                              self.edit_control[SpriteType.BACKGROUND][SpriteSetting.VERTICAL_OFFSET].value,
                                              self.edit_control[SpriteType.BACKGROUND][SpriteSetting.ROTATION].value,
                                              self.edit_control[SpriteType.BACKGROUND][SpriteSetting.ZOOM].value)

        SceneComposer.Jacket.post_process(self.edit_control[SpriteType.JACKET][SpriteSetting.HORIZONTAL_OFFSET].value,
                                          self.edit_control[SpriteType.JACKET][SpriteSetting.VERTICAL_OFFSET].value,
                                          self.edit_control[SpriteType.JACKET][SpriteSetting.ROTATION].value,
                                          self.edit_control[SpriteType.JACKET][SpriteSetting.ZOOM].value)

        SceneComposer.Logo.post_process(self.main_box.has_logo_checkbox.checkState(),
                                        self.edit_control[SpriteType.LOGO][SpriteSetting.HORIZONTAL_OFFSET].value,
                                        self.edit_control[SpriteType.LOGO][SpriteSetting.VERTICAL_OFFSET].value,
                                        self.edit_control[SpriteType.LOGO][SpriteSetting.ROTATION].value,
                                        self.edit_control[SpriteType.LOGO][SpriteSetting.ZOOM].value)

        SceneComposer.Thumbnail.post_process(self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.HORIZONTAL_OFFSET].value,
                                             self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.VERTICAL_OFFSET].value,
                                             self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.ROTATION].value,
                                             self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.ZOOM].value)

    def spinbox_editing_finished_trigger(self,state):
        if state == "on":
            self.edit_control[SpriteType.JACKET][SpriteSetting.HORIZONTAL_OFFSET].editingFinished.connect(self.jacket_value_edit_trigger)
            self.edit_control[SpriteType.JACKET][SpriteSetting.VERTICAL_OFFSET].editingFinished.connect(self.jacket_value_edit_trigger)
            self.edit_control[SpriteType.JACKET][SpriteSetting.ROTATION].editingFinished.connect(self.jacket_value_edit_trigger)
            self.edit_control[SpriteType.JACKET][SpriteSetting.ZOOM].editingFinished.connect(self.jacket_value_edit_trigger)

            self.edit_control[SpriteType.LOGO][SpriteSetting.HORIZONTAL_OFFSET].editingFinished.connect(self.logo_value_edit_trigger)
            self.edit_control[SpriteType.LOGO][SpriteSetting.VERTICAL_OFFSET].editingFinished.connect(self.logo_value_edit_trigger)
            self.edit_control[SpriteType.LOGO][SpriteSetting.ROTATION].editingFinished.connect(self.logo_value_edit_trigger)
            self.edit_control[SpriteType.LOGO][SpriteSetting.ZOOM].editingFinished.connect(self.logo_value_edit_trigger)

            self.edit_control[SpriteType.BACKGROUND][SpriteSetting.HORIZONTAL_OFFSET].editingFinished.connect(self.background_value_edit_trigger)
            self.edit_control[SpriteType.BACKGROUND][SpriteSetting.VERTICAL_OFFSET].editingFinished.connect(self.background_value_edit_trigger)
            self.edit_control[SpriteType.BACKGROUND][SpriteSetting.ROTATION].editingFinished.connect(self.background_value_edit_trigger)
            self.edit_control[SpriteType.BACKGROUND][SpriteSetting.ZOOM].editingFinished.connect(self.background_value_edit_trigger)

            self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.HORIZONTAL_OFFSET].editingFinished.connect(self.thumbnail_value_edit_trigger)
            self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.VERTICAL_OFFSET].editingFinished.connect(self.thumbnail_value_edit_trigger)
            self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.ROTATION].editingFinished.connect(self.thumbnail_value_edit_trigger)
            self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.ZOOM].editingFinished.connect(self.thumbnail_value_edit_trigger)

        else:
            self.edit_control[SpriteType.JACKET][SpriteSetting.HORIZONTAL_OFFSET].editingFinished.disconnect(self.jacket_value_edit_trigger)
            self.edit_control[SpriteType.JACKET][SpriteSetting.VERTICAL_OFFSET].editingFinished.disconnect(self.jacket_value_edit_trigger)
            self.edit_control[SpriteType.JACKET][SpriteSetting.ROTATION].editingFinished.disconnect(self.jacket_value_edit_trigger)
            self.edit_control[SpriteType.JACKET][SpriteSetting.ZOOM].editingFinished.disconnect(self.jacket_value_edit_trigger)

            self.edit_control[SpriteType.LOGO][SpriteSetting.HORIZONTAL_OFFSET].editingFinished.disconnect(self.logo_value_edit_trigger)
            self.edit_control[SpriteType.LOGO][SpriteSetting.VERTICAL_OFFSET].editingFinished.disconnect(self.logo_value_edit_trigger)
            self.edit_control[SpriteType.LOGO][SpriteSetting.ROTATION].editingFinished.disconnect(self.logo_value_edit_trigger)
            self.edit_control[SpriteType.LOGO][SpriteSetting.ZOOM].editingFinished.disconnect(self.logo_value_edit_trigger)

            self.edit_control[SpriteType.BACKGROUND][SpriteSetting.HORIZONTAL_OFFSET].editingFinished.disconnect(self.background_value_edit_trigger)
            self.edit_control[SpriteType.BACKGROUND][SpriteSetting.VERTICAL_OFFSET].editingFinished.disconnect(self.background_value_edit_trigger)
            self.edit_control[SpriteType.BACKGROUND][SpriteSetting.ROTATION].editingFinished.disconnect(self.background_value_edit_trigger)
            self.edit_control[SpriteType.BACKGROUND][SpriteSetting.ZOOM].editingFinished.disconnect(self.background_value_edit_trigger)

            self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.HORIZONTAL_OFFSET].editingFinished.disconnect(self.thumbnail_value_edit_trigger)
            self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.VERTICAL_OFFSET].editingFinished.disconnect(self.thumbnail_value_edit_trigger)
            self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.ROTATION].editingFinished.disconnect(self.thumbnail_value_edit_trigger)
            self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.ZOOM].editingFinished.disconnect(self.thumbnail_value_edit_trigger)

    def watcher_file_modified_action(self,path):
        sleep(2) #TODO replace sleep with detection is the modified file there
        keep_watching_path = False
        if path == SceneComposer.Jacket.location:
            print("Jacket image was changed")
            result = SceneComposer.Jacket.update_sprite(path)
            if result["Outcome"] == State.FALLBACK:
                print("Jacket image no longer meets requirements. Falling back to Dummy sprite")
                self.watcher.addPath(str(SceneComposer.Jacket.dummy_location))
            elif result["Outcome"] == State.UPDATED:
                keep_watching_path = True

                if result["Jacket Force Fit"]:
                    real_width = SceneComposer.Jacket.edges[2] - SceneComposer.Jacket.edges[0]
                    real_height = SceneComposer.Jacket.edges[3] - SceneComposer.Jacket.edges[1]

                    print(f"Image is {real_width}x{real_height}. Imported jacket is 1:1 aspect ratio.")
                    self.edit_control[SpriteType.JACKET][SpriteSetting.ZOOM].setValue(result["Zoom"])
                    print(f"Set jacket's zoom to {result["Zoom"]}.")

        if path == SceneComposer.Logo.location:
            print("Logo image was changed")
            result = SceneComposer.Logo.update_sprite(path)
            if result["Outcome"] == State.UPDATED:
                self.edit_control[SpriteType.LOGO][SpriteSetting.ZOOM].set_range(SceneComposer.Logo.calculate_range(SpriteSetting.ZOOM))
                keep_watching_path = True

        if path == SceneComposer.Background.location:
            print("Background image was changed")
            result = SceneComposer.Background.update_sprite(path)
            if result["Outcome"] == State.FALLBACK:
                print("Background image no longer meets requirements. Falling back to Dummy sprite")
                self.watcher.addPath(str(SceneComposer.Background.dummy_location))
            elif result["Outcome"] == State.UPDATED:
                keep_watching_path = True

        if path == SceneComposer.Thumbnail.location:
            print("Thumbnail image was changed")
            result = SceneComposer.Thumbnail.update_sprite(path)
            if result["Outcome"] == State.FALLBACK:
                print("Thumbnail image no longer meets requirements. Falling back to Dummy sprite")
                self.watcher.addPath(str(SceneComposer.Thumbnail.dummy_location))
            elif result["Outcome"] == State.UPDATED:
                keep_watching_path = True

        if keep_watching_path:
            self.watcher.removePath(path)
            self.watcher.addPath(path)
        else:
            self.watcher.removePath(path)

        self.reload_images()
        self.draw_image_grid()

    def create_background_jacket_texture(self):
        jacket_composite = Image.new('RGBA', (2048, 1024), (0, 0, 0, 0))
        jacket_composite.alpha_composite(SceneComposer.Jacket.jacket, (1286, 2))

        background_composite = Image.new('RGBA', (2048, 1024), (0, 0, 0, 0))
        background_composite.alpha_composite(SceneComposer.Background.background, (1, 1), (0, 0, 1280, 720))
        background_composite = texture_filtering_fix(background_composite,255)

        background_jacket_texture = Image.new('RGBA', (2048, 1024))
        background_jacket_texture.alpha_composite(background_composite)
        background_jacket_texture.alpha_composite(jacket_composite)

        return background_jacket_texture
    def create_logo_texture(self):
        logo_fix_status = False
        if logo_fix_status:
            logo = texture_filtering_fix(SceneComposer.Logo.logo,102)
            x = 1
            y = 1
        else:
            logo = SceneComposer.Logo.logo
            x = 2
            y = 2
        logo_texture = Image.new('RGBA', (1024, 512))
        logo_texture.alpha_composite(logo,(x,y))
        return logo_texture
    def create_thumbnail_texture(self):
        thumbnail_texture = Image.new('RGBA', (128, 64))
        thumbnail_texture.alpha_composite(SceneComposer.Thumbnail.thumbnail)
        return thumbnail_texture


    def export_background_jacket_logo_farc_button_callback(self):
        output_location = QFileDialog.getExistingDirectory(self, "Choose folder to save farc file to", str(config.last_used_directory))

        if output_location == "":
            print("Directory wasn't chosen")
        else:
            config.last_used_directory = Path(output_location)

            Image.Image.save(self.create_background_jacket_texture(), (config.script_directory / 'Images/Background Texture.png'))
            Image.Image.save(self.create_logo_texture(), (config.script_directory / 'Images/Logo Texture.png'))
            song_id = pad_number(int(self.main_box.farc_song_id_spinbox.value()))

            output_location = output_location
            if self.main_box.has_logo_checkbox.checkState() == Qt.CheckState.Checked:
                logo_state = True
            else:
                logo_state = False
            FarcCreator.create_jk_bg_logo_farc(song_id, str(config.script_directory / 'Images/Background Texture.png'), str(config.script_directory / 'Images/Logo Texture.png'), output_location, logo_state)



    def refresh_image_grid(self):
        self.draw_image_grid()

    def has_logo_checkbox_callback(self):
        #TODO Figure out what to do with this shit
        #Needs a better way of removing the tab
        if self.main_box.has_logo_checkbox.checkState() == Qt.CheckState.Checked:
            #Make options to tweak logo visible
            self.main_box.current_sprite_combobox.addItem("Logo")
            #Enable buttons related to logos
            self.main_box.load_logo_button.setEnabled(True)
            self.main_box.export_logo_button.setEnabled(True)
            #Draw Logo
            SceneComposer.Logo.post_process(self.main_box.has_logo_checkbox.checkState(),
                                            self.edit_control[SpriteType.LOGO][SpriteSetting.HORIZONTAL_OFFSET].value,
                                            self.edit_control[SpriteType.LOGO][SpriteSetting.VERTICAL_OFFSET].value,
                                            self.edit_control[SpriteType.LOGO][SpriteSetting.ROTATION].value,
                                            self.edit_control[SpriteType.LOGO][SpriteSetting.ZOOM].value)
            self.draw_image_grid()
        else:
            # Make options to tweak logo invisible
            self.main_box.current_sprite_combobox.removeItem(3)
            #Disable buttons related to logos
            self.main_box.load_logo_button.setDisabled(True)
            self.main_box.export_logo_button.setDisabled(True)
            # Hide Logo
            SceneComposer.Logo.post_process(self.main_box.has_logo_checkbox.checkState(),
                                            self.edit_control[SpriteType.LOGO][SpriteSetting.HORIZONTAL_OFFSET].value,
                                            self.edit_control[SpriteType.LOGO][SpriteSetting.VERTICAL_OFFSET].value,
                                            self.edit_control[SpriteType.LOGO][SpriteSetting.ROTATION].value,
                                            self.edit_control[SpriteType.LOGO][SpriteSetting.ZOOM].value)
            self.draw_image_grid()

    #TODO Simplify loading sprites into single function
    def load_background_button_callback(self):
        open_background = QFileDialog.getOpenFileName(self, "Open background image", str(config.last_used_directory), config.allowed_file_types)[0]

        if open_background == '':
            print("Background image wasn't chosen")
        else:
            try:
                result = SceneComposer.Background.update_sprite(open_background,False)

                if result["Outcome"] == State.UPDATED:
                    SceneComposer.Background.flipped_h = False
                    SceneComposer.Background.flipped_v = False
                    config.last_used_directory = Path(open_background).parent

                    self.watcher.removePath(str(SceneComposer.Background.location))
                    self.watcher.addPath(str(SceneComposer.Background.location))

                    self.spinbox_editing_finished_trigger("off")

                    for control in self.edit_control[SpriteType.BACKGROUND]:
                        self.edit_control[SpriteType.BACKGROUND][control].reset_value()

                    SceneComposer.Background.post_process(self.edit_control[SpriteType.BACKGROUND][SpriteSetting.HORIZONTAL_OFFSET].value,
                                                          self.edit_control[SpriteType.BACKGROUND][SpriteSetting.VERTICAL_OFFSET].value,
                                                          self.edit_control[SpriteType.BACKGROUND][SpriteSetting.ROTATION].value,
                                                          self.edit_control[SpriteType.BACKGROUND][SpriteSetting.ZOOM].value)

                    self.edit_control[SpriteType.BACKGROUND][SpriteSetting.ZOOM].set_range(SceneComposer.Background.calculate_range(SpriteSetting.ZOOM))
                    self.edit_control[SpriteType.BACKGROUND][SpriteSetting.HORIZONTAL_OFFSET].set_range(SceneComposer.Background.calculate_range(SpriteSetting.HORIZONTAL_OFFSET))
                    self.edit_control[SpriteType.BACKGROUND][SpriteSetting.VERTICAL_OFFSET].set_range(SceneComposer.Background.calculate_range(SpriteSetting.VERTICAL_OFFSET))

                    self.spinbox_editing_finished_trigger("on")

                    self.draw_image_grid()

                elif result["Outcome"] == State.IMAGE_TOO_SMALL:
                    config.last_used_directory = Path(open_background).parent
                    show_message_box(result["Window Title"], result["Description"])
            except PIL.UnidentifiedImageError:
                config.last_used_directory = Path(open_background).parent
                print("Couldn't load image. Image might be corrupted")
    def load_jacket_button_callback(self):
        open_jacket = QFileDialog.getOpenFileName(self,"Open jacket image", str(config.last_used_directory), config.allowed_file_types)[0]

        if open_jacket == '':
            print("Jacket image wasn't chosen")
        else:
            try:
                result = SceneComposer.Jacket.update_sprite(open_jacket,False)

                if result["Outcome"] == State.UPDATED:
                    SceneComposer.Jacket.flipped_h = False
                    SceneComposer.Jacket.flipped_v = False
                    config.last_used_directory = Path(open_jacket).parent

                    self.watcher.removePath(str(SceneComposer.Jacket.location))
                    self.watcher.addPath(str(SceneComposer.Jacket.location))

                    self.spinbox_editing_finished_trigger("off")

                    for control in self.edit_control[SpriteType.JACKET]:
                        self.edit_control[SpriteType.JACKET][control].reset_value()

                    SceneComposer.Jacket.post_process(self.edit_control[SpriteType.JACKET][SpriteSetting.HORIZONTAL_OFFSET].value,
                                                      self.edit_control[SpriteType.JACKET][SpriteSetting.VERTICAL_OFFSET].value,
                                                      self.edit_control[SpriteType.JACKET][SpriteSetting.ROTATION].value,
                                                      self.edit_control[SpriteType.JACKET][SpriteSetting.ZOOM].value)
                    if result["Jacket Force Fit"]:
                        print(f"Image is {SceneComposer.Jacket.jacket_image.width}x{SceneComposer.Jacket.jacket_image.height}. Imported jacket is 1:1 aspect ratio.")
                        self.edit_control[SpriteType.JACKET][SpriteSetting.ZOOM].setValue(result["Zoom"])
                        print(f"Set jacket's zoom to {result["Zoom"]}.")
                    else:
                        self.edit_control[SpriteType.JACKET][SpriteSetting.ZOOM].set_range(SceneComposer.Jacket.calculate_range(SpriteSetting.ZOOM))

                    self.edit_control[SpriteType.JACKET][SpriteSetting.HORIZONTAL_OFFSET].set_range(SceneComposer.Jacket.calculate_range(SpriteSetting.HORIZONTAL_OFFSET))
                    self.edit_control[SpriteType.JACKET][SpriteSetting.VERTICAL_OFFSET].set_range(SceneComposer.Jacket.calculate_range(SpriteSetting.VERTICAL_OFFSET))

                    self.spinbox_editing_finished_trigger("on")

                    self.draw_image_grid()

                elif result["Outcome"] == State.IMAGE_TOO_SMALL:
                    config.last_used_directory = Path(open_jacket).parent
                    show_message_box(result["Window Title"], result["Description"])
            except PIL.UnidentifiedImageError:
                config.last_used_directory = Path(open_jacket).parent
                print("Couldn't load image. Image might be corrupted")
    def load_logo_button_callback(self):
        open_logo = QFileDialog.getOpenFileName(self, "Open logo image", str(config.last_used_directory), config.allowed_file_types)[0]

        if open_logo == '':
            print("Logo image wasn't chosen")
        else:
            try:
                result = SceneComposer.Logo.update_sprite(open_logo,False)

                if result["Outcome"] == State.UPDATED:
                    SceneComposer.Logo.flipped_h = False
                    SceneComposer.Logo.flipped_v = False
                    config.last_used_directory = Path(open_logo).parent

                    self.watcher.removePath(str(SceneComposer.Logo.location))
                    self.watcher.addPath(str(SceneComposer.Logo.location))

                    for control in self.edit_control[SpriteType.LOGO]:
                        self.edit_control[SpriteType.LOGO][control].reset_value()

                    SceneComposer.Logo.post_process(self.main_box.has_logo_checkbox.checkState(),
                                                    self.edit_control[SpriteType.LOGO][SpriteSetting.HORIZONTAL_OFFSET].value,
                                                    self.edit_control[SpriteType.LOGO][SpriteSetting.VERTICAL_OFFSET].value,
                                                    self.edit_control[SpriteType.LOGO][SpriteSetting.ROTATION].value,
                                                    self.edit_control[SpriteType.LOGO][SpriteSetting.ZOOM].value)

                    self.edit_control[SpriteType.LOGO][SpriteSetting.ZOOM].set_range(SceneComposer.Logo.calculate_range(SpriteSetting.ZOOM))
                    self.edit_control[SpriteType.LOGO][SpriteSetting.HORIZONTAL_OFFSET].set_range(SceneComposer.Logo.calculate_range(SpriteSetting.HORIZONTAL_OFFSET))
                    self.edit_control[SpriteType.LOGO][SpriteSetting.VERTICAL_OFFSET].set_range(SceneComposer.Logo.calculate_range(SpriteSetting.VERTICAL_OFFSET))

                    self.draw_image_grid()
            except PIL.UnidentifiedImageError:
                config.last_used_directory = Path(open_logo).parent
                print("Couldn't load image. Image might be corrupted")
    def load_thumbnail_button_callback(self):
        open_thumbnail = QFileDialog.getOpenFileName(self, "Open thumbnail image", str(config.last_used_directory), config.allowed_file_types)[0]

        if open_thumbnail == '':
            print("Thumbnail image wasn't chosen")
        else:
            try:
                result = SceneComposer.Thumbnail.update_sprite(open_thumbnail,False)

                if result["Outcome"] == State.UPDATED:
                    SceneComposer.Thumbnail.flipped_h = False
                    SceneComposer.Thumbnail.flipped_v = False
                    config.last_used_directory = Path(open_thumbnail).parent

                    self.watcher.removePath(str(SceneComposer.Thumbnail.location))
                    self.watcher.addPath(str(SceneComposer.Thumbnail.location))

                    for control in self.edit_control[SpriteType.THUMBNAIL]:
                        self.edit_control[SpriteType.THUMBNAIL][control].reset_value()

                    SceneComposer.Thumbnail.post_process(self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.HORIZONTAL_OFFSET].value,
                                                         self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.VERTICAL_OFFSET].value,
                                                         self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.ROTATION].value,
                                                         self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.ZOOM].value)

                    self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.ZOOM].set_range(SceneComposer.Thumbnail.calculate_range(SpriteSetting.ZOOM))
                    self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.HORIZONTAL_OFFSET].set_range(SceneComposer.Thumbnail.calculate_range(SpriteSetting.HORIZONTAL_OFFSET))
                    self.edit_control[SpriteType.THUMBNAIL][SpriteSetting.VERTICAL_OFFSET].set_range(SceneComposer.Thumbnail.calculate_range(SpriteSetting.VERTICAL_OFFSET))

                    self.draw_image_grid()
                    self.thumbnail_q = SceneComposer.Thumbnail.thumbnail_image.toqimage().convertToFormat(QImage.Format.Format_ARGB32_Premultiplied)
                    self.thumbnail.setPixmap(QPixmap(self.thumbnail_q))

                elif result["Outcome"] == State.IMAGE_TOO_SMALL:
                    config.last_used_directory = Path(open_thumbnail).parent
                    show_message_box(result["Window Title"], result["Description"])
            except PIL.UnidentifiedImageError:
                config.last_used_directory = Path(open_thumbnail).parent
                print("Couldn't load image. Image might be corrupted")

    def load_new_sprite_image(self,sprite:QSpriteBase):
        #TODO Get all objects with specified sprite type.
        #TODO make watcher functional
        #Open file explorer to select file
        #Test the image against required sizes
        #Apply the image if it fits
        image_location = QFileDialog.getOpenFileName(self,
                                                 f"Open {sprite.type.value} image",
                                                 str(config.last_used_directory),
                                                 config.allowed_file_types)[0]

        sprite.load_new_image(image_location)

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
            thumbnail_texture.save(save_location, "png")

    def export_logo_button_callback(self):
        save_location = QFileDialog.getSaveFileName(self, "Save File", str(config.last_used_directory) + "/Logo Texture.png", "Images (*.png)")[0]

        if save_location == "":
            print("Directory wasn't chosen")
        else:
            config.last_used_directory = Path(save_location).parent
            logo_texture = self.create_logo_texture()
            logo_texture.save(save_location, "png")

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
                if has_new_tmb_farc == True:
                    if has_old_tmb_farc == True:
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
    SceneComposer = SceneComposer()
    FarcCreator = FarcCreator()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    main_window = MainWindow()
    main_window.show()
    app.exec()