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
import filedialpy
from PySide6.QtCore import Qt, Slot, QFileSystemWatcher, QSize, Signal
from PySide6.QtGui import QPixmap, QPalette, QColor
from PySide6.QtWidgets import QApplication, QMessageBox, QMainWindow, QWidget, QFrame
from PIL import Image,ImageShow,ImageStat
from PIL.ImageShow import Viewer

from concurrent.futures import ThreadPoolExecutor

from copykitten import copy_image
from filedialpy import openFile
from decimal import Decimal, ROUND_HALF_UP

from SceneComposer import SceneComposer, State, SpriteType, Scene
from FarcCreator import FarcCreator
from auto_creat_mod_spr_db import Manager, add_farc_to_Manager, read_farc

from ui_ThumbnailTextureCreator import Ui_ThumbnailTextureCreator
from ui_ThumbnailWidget import Ui_ThumbnailWidget
from ui_ThumbnailIDField import  Ui_ThumbnailIDField
from ui_SpriteHelper import Ui_MainWindow

from widgets import Stylesheet

class OutputTarget(Enum):
    CLIPBOARD = auto()
    IMAGE_VIEWER = auto()
    IMAGE = auto()

class Configurable:
    def __init__(self):
        self.script_directory = Path.cwd()
        self.allowed_file_types = ["*.png *.jpg *.jpeg *.webp"] #TODO get supported file types in smarter way
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


class ThumbnailWindow(QWidget):
    resized = Signal()
    spr_db_button_clicked = Signal()
    def __init__(self):
        super(ThumbnailWindow, self).__init__()
        self.main_box = Ui_ThumbnailTextureCreator()
        self.main_box.setupUi(self)
        self.main_box.load_folder_button.clicked.connect(self.scan_folder_for_thumbnails)
        self.main_box.export_farc_button.clicked.connect(self.create_thumbnail_farc)
        self.main_box.load_image_button.clicked.connect(self.update_thumbnail_count_labels)
        self.main_box.generate_spr_db_button.clicked.connect(self.spr_db_button_clicked.emit)
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
        else:
            self.main_box.export_farc_button.setDisabled(False)
            self.main_box.export_farc_button.setToolTip("")

    def add_thumbnail(self,image_path,inferred_id):
        if self.thumbnail_widgets:
            for thumbnail in self.thumbnail_widgets:
                if image_path == thumbnail.image_path:
                    return

        #
        # for entry in main_window.thumbnail_creator.known_ids:
        #     if str(image_path) == entry[0]:
        #         thumbnail_widget = ThumbnailWidget(image_path=image_path, inferred_id=entry[1])
        #         print(f"inferring {entry[1]} from YAML")
        #         break
        #
        # if thumbnail_widget is None:
        #     if Path(image_path).stem.isdigit() and len(Path(image_path).stem) >= 3:
        #         id_list = [Path(image_path).stem]
        #         thumbnail_widget = ThumbnailWidget(image_path=image_path, inferred_id=id_list)
        #         #print(f"inferring {id_list} from file name")
        #     else:
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
            with io.open('remembered_ids.yaml', 'r') as infile:
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

    def scan_folder_for_thumbnails(self):
        if os.name == "nt":
            selected_folder = filedialpy.openDir(title="Choose folder containing thumbnails")
        else:
            selected_folder = filedialpy.openDir(title="Choose folder containing thumbnails", initial_dir=config.last_used_directory)

            if selected_folder == "":
                print("Folder wasn't selected")
            else:
                config.last_used_directory = Path(selected_folder)
                start_time = time.time()

                with ThreadPoolExecutor(max_workers=1) as executor:  # This was a waste of time to add...
                    futures = []

                    if self.main_box.search_subfolders_checkbox.checkState() == Qt.CheckState.Checked:
                        for path in Path(selected_folder).rglob('*.png'):
                            with Image.open(path) as open_image:
                                if open_image.size == (128,64):
                                    futures.append(executor.submit(self.infer_thumbnail_id, path))
                    else:
                        for path in Path(selected_folder).glob('*.png'):
                            with Image.open(path) as open_image:
                                if open_image.size == (128, 64):
                                    futures.append(executor.submit(self.infer_thumbnail_id, path))

                results = [future.result() for future in futures]
                for widget in results:
                    self.add_thumbnail(widget[0][0],widget[0][1])


                self.space_out_thumbnails()
                self.update_thumbnail_count_labels()
                #print("--- %s seconds ---" % (time.time() - start_time))

    def create_thumbnail_farc(self):
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
                thumbnail_positions.append([self.pad_number(thumb_id), (x, y)])

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

        if os.name == "nt":
            chosen_dir = filedialpy.openDir(title="Choose folder to save farc file to")
        else:
            chosen_dir = filedialpy.openDir(title="Choose folder to save farc file to", initial_dir=config.last_used_directory)

        if chosen_dir == "":
            print("Folder wasn't chosen")
        else:
            config.last_used_directory = Path(chosen_dir)

            thumbnail_texture.save(str(config.script_directory) + "/Images/Thumbnail Texture.png","png")
            mod_name = self.get_song_pack_name()
            FarcCreator.create_thumbnail_farc(thumbnail_positions,str(config.script_directory) + "/Images/Thumbnail Texture.png",chosen_dir,mod_name)

            #Remember ID's used for images

            #TODO
            #Needs to be formatted into:
            # File path
            #   [ID,ID,ID...]
            #Needs to overwrite already existing entries for the file path , but keep others untouched
            remember_data = []
            for thumb_widget in self.thumbnail_widgets:
                image = str(thumb_widget.image_path)
                ids = []
                for id_field in thumb_widget.id_field_list:
                    ids.append(int(id_field.ui.song_id_spinbox.value()))
                remember_data.append([image,ids])

            if Path('remembered_ids.yaml').exists():
                with io.open('remembered_ids.yaml', 'r') as infile:
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

            total_height = rows * 66
            tex_height = self.next_power_of_two(total_height)
            area = (tex_width , tex_height)
        return area

    def get_song_pack_name(self):
        mod_string = self.main_box.mod_name_lineedit.text()
        mod_string = mod_string.translate(str.maketrans('', '', string.punctuation)).lower()
        mod_string = re.sub(r'[^A-Za-z0-9 ]+', '',mod_string)

        return "_".join(mod_string.split())

    def pad_number(self,number):
        if number >= 100:
            return str(number)
        elif number >= 10:
            return "0"+ str(number)
        else:
            return "00" + str(number)

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
    composite.alpha_composite(SceneComposer.compose_scene(Scene.MEGAMIX_SONG_SELECT,new_classics_state), (0, 0))
    composite.alpha_composite(SceneComposer.compose_scene(Scene.MEGAMIX_RESULT,new_classics_state), (0, 1080))
    composite.alpha_composite(SceneComposer.compose_scene(Scene.FUTURE_TONE_SONG_SELECT,new_classics_state), (1920, 0))
    composite.alpha_composite(SceneComposer.compose_scene(Scene.FUTURE_TONE_RESULT,new_classics_state), (1920, 1080))

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
        self.main_box.load_thumbnail_button.clicked.connect(self.load_thumbnail_button_callback)
        self.main_box.load_logo_button.clicked.connect(self.load_logo_button_callback)
        self.main_box.load_jacket_button.clicked.connect(self.load_jacket_button_callback)
        self.main_box.copy_to_clipboard_button.clicked.connect(lambda: draw_combined_preview_to(OutputTarget.CLIPBOARD))
        self.main_box.open_preview_button.clicked.connect(lambda: draw_combined_preview_to(OutputTarget.IMAGE_VIEWER))
        self.main_box.export_background_jacket_button.clicked.connect(self.export_background_jacket_button_callback)
        self.main_box.export_thumbnail_button.clicked.connect(self.export_thumbnail_button_callback)
        self.main_box.export_logo_button.clicked.connect(self.export_logo_button_callback)
        self.main_box.generate_spr_db_button.clicked.connect(self.generate_spr_db_button_callback)
        self.main_box.farc_create_thumbnail_button.clicked.connect(self.farc_create_thumbnail_button_callback)
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

        self.thumbnail_creator.spr_db_button_clicked.connect(self.generate_spr_db_button_callback)

        self.current_sprite_tab_switcher(self.main_box.current_sprite_combobox.currentIndex()) # Make sure that tab matches options shown on start
        self.draw_image_grid()

    def resizeEvent(self,event):
        #Todo allow resizing by grabbing top/bottom edge too

        # Force 2:1 aspect ratio
        new_width = self.size().width()
        new_height = int(new_width / 2)
        size = QSize(new_width,new_height)
        self.resize(size)
    @Slot()
    def current_sprite_tab_switcher(self,tab):
        self.main_box.sprite_controls.setCurrentIndex(tab)

    @Slot()
    def view_pixmap_external(self,scene):
        #TODO use pixmap.save to not re-render scene
        new_classics_state = main_window.main_box.new_classics_checkbox.isChecked()
        match scene:
            case Scene.MEGAMIX_SONG_SELECT:
                ImageShow.show(SceneComposer.compose_scene(Scene.MEGAMIX_SONG_SELECT,new_classics_state))
            case Scene.FUTURE_TONE_SONG_SELECT:
                ImageShow.show(SceneComposer.compose_scene(Scene.FUTURE_TONE_SONG_SELECT, new_classics_state))
            case Scene.MEGAMIX_RESULT:
                ImageShow.show(SceneComposer.compose_scene(Scene.MEGAMIX_RESULT, new_classics_state))
            case Scene.FUTURE_TONE_RESULT:
                ImageShow.show(SceneComposer.compose_scene(Scene.FUTURE_TONE_RESULT, new_classics_state))

    def draw_scene(self, ui_scene):
        new_classics_state = self.main_box.new_classics_checkbox.isChecked()
        match ui_scene:
            case Scene.MEGAMIX_SONG_SELECT:
                self.main_box.mm_song_selector_preview.setPixmap(SceneComposer.compose_scene(ui_scene,new_classics_state).toqpixmap())
            case Scene.FUTURE_TONE_SONG_SELECT:
                self.main_box.ft_song_selector_preview.setPixmap(SceneComposer.compose_scene(ui_scene,new_classics_state).toqpixmap())
            case Scene.MEGAMIX_RESULT:
                self.main_box.mm_result_preview.setPixmap(SceneComposer.compose_scene(ui_scene,new_classics_state).toqpixmap())
            case Scene.FUTURE_TONE_RESULT:
                self.main_box.ft_result_preview.setPixmap(SceneComposer.compose_scene(ui_scene,new_classics_state).toqpixmap())
    def draw_image_grid(self):
        for scene in config.scenes_to_draw:
            self.draw_scene(scene)

        Jacket_state = SceneComposer.check_sprite(SpriteType.JACKET)
        Background_state = SceneComposer.check_sprite(SpriteType.BACKGROUND)

        if Jacket_state == False or Background_state == False:
            failed_check = []
            if Jacket_state == False:
                print("Jacket is fucked up")
                failed_check.append("Jacket")
            else:
                print("Jacket is fine")
            if Background_state == False:
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

        if Thumbnail_state == False:
            print("Thumbnail is fucked up")
            self.main_box.export_thumbnail_button.setEnabled(False)
            self.main_box.export_thumbnail_button.setToolTip("Thumbnail isn't fully filled by opaque image!")
        else:
            print("Thumbnail is fine")
            self.main_box.export_thumbnail_button.setEnabled(True)
            self.main_box.export_thumbnail_button.setToolTip("")

    def jacket_value_edit_trigger(self):
        SceneComposer.Jacket.post_process(self.main_box.jacket_horizontal_offset_spinbox.value(),self.main_box.jacket_vertical_offset_spinbox.value(),self.main_box.jacket_rotation_spinbox.value(),self.main_box.jacket_zoom_spinbox.value())
        self.change_spinbox_offset_range(SpriteType.JACKET)
        SceneComposer.Jacket.post_process(self.main_box.jacket_horizontal_offset_spinbox.value(),self.main_box.jacket_vertical_offset_spinbox.value(),self.main_box.jacket_rotation_spinbox.value(),self.main_box.jacket_zoom_spinbox.value())
        self.draw_image_grid()
    def logo_value_edit_trigger(self):
        SceneComposer.Logo.post_process(self.main_box.has_logo_checkbox.checkState(),self.main_box.logo_horizontal_offset_spinbox.value(), self.main_box.logo_vertical_offset_spinbox.value(), self.main_box.logo_rotation_spinbox.value(), self.main_box.logo_zoom_spinbox.value())
        self.change_spinbox_offset_range(SpriteType.LOGO)
        SceneComposer.Logo.post_process(self.main_box.has_logo_checkbox.checkState(),self.main_box.logo_horizontal_offset_spinbox.value(), self.main_box.logo_vertical_offset_spinbox.value(), self.main_box.logo_rotation_spinbox.value(), self.main_box.logo_zoom_spinbox.value())
        self.draw_image_grid()
    def background_value_edit_trigger(self):
        SceneComposer.Background.post_process(self.main_box.background_horizontal_offset_spinbox.value(), self.main_box.background_vertical_offset_spinbox.value(), self.main_box.background_rotation_spinbox.value(), self.main_box.background_zoom_spinbox.value())
        self.change_spinbox_offset_range(SpriteType.BACKGROUND)
        SceneComposer.Background.post_process(self.main_box.background_horizontal_offset_spinbox.value(), self.main_box.background_vertical_offset_spinbox.value(), self.main_box.background_rotation_spinbox.value(), self.main_box.background_zoom_spinbox.value())
        self.draw_image_grid()
    def thumbnail_value_edit_trigger(self):
        SceneComposer.Thumbnail.post_process(self.main_box.thumbnail_horizontal_offset_spinbox.value(), self.main_box.thumbnail_vertical_offset_spinbox.value(), self.main_box.thumbnail_rotation_spinbox.value(), self.main_box.thumbnail_zoom_spinbox.value())
        self.change_spinbox_offset_range(SpriteType.THUMBNAIL)
        SceneComposer.Thumbnail.post_process(self.main_box.thumbnail_horizontal_offset_spinbox.value(), self.main_box.thumbnail_vertical_offset_spinbox.value(), self.main_box.thumbnail_rotation_spinbox.value(), self.main_box.thumbnail_zoom_spinbox.value())
        self.draw_image_grid()

    def reload_images(self):
        SceneComposer.Background.post_process(self.main_box.background_horizontal_offset_spinbox.value(), self.main_box.background_vertical_offset_spinbox.value(), self.main_box.background_rotation_spinbox.value(), self.main_box.background_zoom_spinbox.value())
        SceneComposer.Jacket.post_process(self.main_box.jacket_horizontal_offset_spinbox.value(), self.main_box.jacket_vertical_offset_spinbox.value(), self.main_box.jacket_rotation_spinbox.value(), self.main_box.jacket_zoom_spinbox.value())
        SceneComposer.Logo.post_process(self.main_box.has_logo_checkbox.checkState(), self.main_box.logo_horizontal_offset_spinbox.value(), self.main_box.logo_vertical_offset_spinbox.value(), self.main_box.logo_rotation_spinbox.value(), self.main_box.logo_zoom_spinbox.value())
        SceneComposer.Thumbnail.post_process(self.main_box.thumbnail_horizontal_offset_spinbox.value(), self.main_box.thumbnail_vertical_offset_spinbox.value(), self.main_box.thumbnail_rotation_spinbox.value(), self.main_box.thumbnail_zoom_spinbox.value())
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

    def fit_logo(self,logo_image):
        with Image.open(logo_image).convert('RGBA') as logo:
            left, upper, right, lower = Image.Image.getbbox(logo)
            image_width = right - left
            image_height = lower - upper

            if image_height > 330 or image_width > 870:
                if (330 / image_height) <= (870 / image_width):
                    max_scale = 330 / image_height
                else:
                    max_scale = 870 / image_width
            else:
                max_scale = 1
        self.main_box.logo_zoom_spinbox.setMaximum(max_scale)

    def change_spinbox_offset_range(self,spinbox):
        match spinbox:
            case SpriteType.JACKET:
                minimum_horizontal = (SceneComposer.Jacket.jacket_image.width * -1) + 500
                minimum_vertical = (SceneComposer.Jacket.jacket_image.height * -1) + 500
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
            case SpriteType.BACKGROUND:
                minimum_horizontal = (SceneComposer.Background.background_image.width * -1) + 1280
                minimum_vertical = (SceneComposer.Background.background_image.height * -1) + 720
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
            case SpriteType.LOGO:
                with SceneComposer.Logo.logo_image as logo:
                    left, upper, right , lower = Image.Image.getbbox(logo)

                    logo_max_width_offset = 870 - right
                    logo_max_height_offset = 330 - lower

                    self.main_box.logo_horizontal_offset_spinbox.setRange(-left,logo_max_width_offset)
                    self.main_box.logo_vertical_offset_spinbox.setRange(-upper,logo_max_height_offset)
            case SpriteType.THUMBNAIL:
                minimum_horizontal = (SceneComposer.Thumbnail.thumbnail_image.width * -1) + 100
                minimum_vertical = (SceneComposer.Thumbnail.thumbnail_image.height * -1) + 61
                self.main_box.thumbnail_horizontal_offset_spinbox.setRange(minimum_horizontal ,0)
                self.main_box.thumbnail_vertical_offset_spinbox.setRange(minimum_vertical,0)

                if minimum_horizontal == 0:
                    self.main_box.thumbnail_horizontal_offset_spinbox.setEnabled(False)
                else:
                    self.main_box.thumbnail_horizontal_offset_spinbox.setEnabled(True)

                if minimum_vertical == 0:
                    self.main_box.thumbnail_vertical_offset_spinbox.setEnabled(False)
                else:
                    self.main_box.thumbnail_vertical_offset_spinbox.setEnabled(True)

    def change_spinbox_zoom_range(self,spinbox,image_width,image_height):
        match spinbox:
            case SpriteType.JACKET:
                width_factor =  Decimal(500 / image_width)
                height_factor = Decimal(500 / image_height)
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

            case SpriteType.BACKGROUND:
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
            case SpriteType.THUMBNAIL:
                width_factor = Decimal(100 / image_width)
                height_factor = Decimal(61 / image_height)
                print(f"Width Factor= {width_factor}")
                print(f"Height Factor= {height_factor}")
                if width_factor > height_factor:
                    self.main_box.thumbnail_zoom_spinbox.setEnabled(True)
                    self.main_box.thumbnail_zoom_spinbox.setRange(width_factor.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP), 1.00)
                elif width_factor < height_factor:
                    self.main_box.thumbnail_zoom_spinbox.setEnabled(True)
                    self.main_box.thumbnail_zoom_spinbox.setRange(height_factor.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP), 1.00)
                else:
                    self.main_box.thumbnail_zoom_spinbox.setEnabled(False)
                    self.main_box.thumbnail_zoom_spinbox.setRange(1.00, 1.00)

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
                    self.main_box.jacket_zoom_spinbox.setValue(result["Zoom"])
                    print(f"Set jacket's zoom to {result["Zoom"]}.")

        if path == SceneComposer.Logo.location:
            print("Logo image was changed")
            result = SceneComposer.Logo.update_sprite(path)
            if result["Outcome"] == State.UPDATED:
                self.fit_logo(path)
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


    @Slot()
    def refresh_image_grid(self):
        for scene in config.scenes_to_draw:
            self.draw_scene(scene)

    @Slot()
    def farc_create_thumbnail_button_callback(self):
        self.thumbnail_creator.show()
    @Slot()
    def has_logo_checkbox_callback(self):
        if self.main_box.has_logo_checkbox.checkState() == Qt.CheckState.Checked:
            #Make options to tweak logo visible
            self.main_box.current_sprite_combobox.addItem("Logo")
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
            SceneComposer.Logo.post_process(self.main_box.has_logo_checkbox.checkState(),self.main_box.logo_horizontal_offset_spinbox.value(), self.main_box.logo_vertical_offset_spinbox.value(), self.main_box.logo_rotation_spinbox.value(), self.main_box.logo_zoom_spinbox.value())
            for scene in config.scenes_to_draw:
                self.draw_scene(scene)
        else:
            # Make options to tweak logo invisible
            self.main_box.current_sprite_combobox.removeItem(3)
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
            SceneComposer.Logo.post_process(self.main_box.has_logo_checkbox.checkState(),self.main_box.logo_horizontal_offset_spinbox.value(), self.main_box.logo_vertical_offset_spinbox.value(), self.main_box.logo_rotation_spinbox.value(), self.main_box.logo_zoom_spinbox.value())
            for scene in config.scenes_to_draw:
                self.draw_scene(scene)
    @Slot()
    def load_background_button_callback(self):
        if os.name == "nt":
            open_background = openFile(title="Open background image", filter=config.allowed_file_types)
        else:
            open_background = openFile(title="Open background image", initial_dir=config.last_used_directory, filter=config.allowed_file_types)

        if open_background == '':
            print("Background image wasn't chosen")
        else:
            result = SceneComposer.Background.update_sprite(open_background,False)

            if result["Outcome"] == State.UPDATED:
                real_width = SceneComposer.Background.edges[2] - SceneComposer.Background.edges[0]
                real_height = SceneComposer.Background.edges[3] - SceneComposer.Background.edges[1]

                config.last_used_directory = Path(open_background).parent
                self.watcher.removePath(str(SceneComposer.Background.location))
                self.change_spinbox_zoom_range(SpriteType.BACKGROUND, real_width, real_height)
                self.watcher.addPath(str(SceneComposer.Background.location))
                self.background_spinbox_values_reset()
                SceneComposer.Background.post_process(self.main_box.background_horizontal_offset_spinbox.value(), self.main_box.background_vertical_offset_spinbox.value(), self.main_box.background_rotation_spinbox.value(), self.main_box.background_zoom_spinbox.value())
                self.change_spinbox_offset_range(SpriteType.BACKGROUND)

                self.draw_image_grid()
            elif result["Outcome"] == State.IMAGE_TOO_SMALL:
                config.last_used_directory = Path(open_background).parent
                show_message_box(result["Window Title"], result["Description"])


    @Slot()
    def load_jacket_button_callback(self):
        if os.name == "nt":
            open_jacket = openFile(title="Open jacket image", filter=config.allowed_file_types)
        else:
            open_jacket = openFile(title="Open jacket image", initial_dir=config.last_used_directory, filter=config.allowed_file_types)

        if open_jacket == '':
            print("Jacket image wasn't chosen")
        else:
            result = SceneComposer.Jacket.update_sprite(open_jacket,False)

            if result["Outcome"] == State.UPDATED:
                real_width = SceneComposer.Jacket.edges[2] - SceneComposer.Jacket.edges[0]
                real_height = SceneComposer.Jacket.edges[3] - SceneComposer.Jacket.edges[1]

                config.last_used_directory = Path(open_jacket).parent
                self.watcher.removePath(str(SceneComposer.Jacket.location))
                self.change_spinbox_zoom_range(SpriteType.JACKET, real_width, real_height)
                self.watcher.addPath(str(SceneComposer.Jacket.location))
                self.jacket_spinbox_values_reset()

                if result["Jacket Force Fit"]:
                    print(f"Image is {real_width}x{real_height}. Imported jacket is 1:1 aspect ratio.")
                    self.main_box.jacket_zoom_spinbox.setValue(result["Zoom"])
                    print(f"Set jacket's zoom to {result["Zoom"]}.")

                SceneComposer.Jacket.post_process(self.main_box.jacket_horizontal_offset_spinbox.value(),self.main_box.jacket_vertical_offset_spinbox.value(),self.main_box.jacket_rotation_spinbox.value(),self.main_box.jacket_zoom_spinbox.value())
                self.change_spinbox_offset_range(SpriteType.JACKET)
                self.draw_image_grid()

            elif result["Outcome"] == State.IMAGE_TOO_SMALL:
                config.last_used_directory = Path(open_jacket).parent
                show_message_box(result["Window Title"], result["Description"])

    @Slot()
    def load_logo_button_callback(self):
        if os.name == "nt":
            open_logo = openFile(title="Open logo image", filter=config.allowed_file_types)
        else:
            open_logo = openFile(title="Open logo image", initial_dir=config.last_used_directory, filter=config.allowed_file_types)
        if open_logo == '':
            print("Logo image wasn't chosen")
        else:
            result = SceneComposer.Logo.update_sprite(open_logo,False)

            if result["Outcome"] == State.UPDATED:
                config.last_used_directory = Path(open_logo).parent
                self.watcher.removePath(str(SceneComposer.Logo.location))
                self.fit_logo(open_logo)
                self.watcher.addPath(str(SceneComposer.Logo.location))
                self.logo_spinbox_values_reset()
                SceneComposer.Logo.post_process(self.main_box.has_logo_checkbox.checkState(),self.main_box.logo_horizontal_offset_spinbox.value(), self.main_box.logo_vertical_offset_spinbox.value(), self.main_box.logo_rotation_spinbox.value(), self.main_box.logo_zoom_spinbox.value())
                self.change_spinbox_offset_range(SpriteType.LOGO)
                self.draw_image_grid()
    @Slot()
    def load_thumbnail_button_callback(self):
        if os.name == "nt":
            open_thumbnail = openFile(title="Open thumbnail image", filter=config.allowed_file_types)
        else:
            open_thumbnail = openFile(title="Open thumbnail image", initial_dir=config.last_used_directory, filter=config.allowed_file_types)
        if open_thumbnail == '':
            print("Thumbnail image wasn't chosen")
        else:
            result = SceneComposer.Thumbnail.update_sprite(open_thumbnail,False)

            if result["Outcome"] == State.UPDATED:
                real_width = SceneComposer.Thumbnail.edges[2] - SceneComposer.Thumbnail.edges[0]
                real_height = SceneComposer.Thumbnail.edges[3] - SceneComposer.Thumbnail.edges[1]

                config.last_used_directory = Path(open_thumbnail).parent
                self.watcher.removePath(str(SceneComposer.Thumbnail.location))
                print(f"W= {real_width} H= {real_height}")
                self.change_spinbox_zoom_range(SpriteType.THUMBNAIL, real_width, real_height)
                self.watcher.addPath(str(SceneComposer.Thumbnail.location))
                self.thumbnail_spinbox_values_reset()
                SceneComposer.Thumbnail.post_process(self.main_box.thumbnail_horizontal_offset_spinbox.value(), self.main_box.thumbnail_vertical_offset_spinbox.value(), self.main_box.thumbnail_rotation_spinbox.value(), self.main_box.thumbnail_zoom_spinbox.value())
                self.change_spinbox_offset_range(SpriteType.THUMBNAIL)
                self.draw_image_grid()

            elif result["Outcome"] == State.IMAGE_TOO_SMALL:
                config.last_used_directory = Path(open_thumbnail).parent
                show_message_box(result["Window Title"], result["Description"])


    @Slot()
    def export_background_jacket_button_callback(self):
        background_jacket_texture = self.create_background_jacket_texture()
        if os.name == "nt":
            save_location = filedialpy.saveFile(initial_file="Background Texture.png", filter="*.png")
        else:
            save_location = filedialpy.saveFile(initial_file="Background Texture.png", initial_dir=config.last_used_directory, filter="*.png")
        if save_location == "":
            print("Directory wasn't chosen")
        else:
            config.last_used_directory = Path(save_location).parent
            background_jacket_texture.save(save_location,"png")
    @Slot()
    def export_thumbnail_button_callback(self):
        thumbnail_texture = self.create_thumbnail_texture()
        if os.name == "nt":
            save_location = filedialpy.saveFile(initial_file="Thumbnail Texture.png",filter="*.png")
        else:
            save_location = filedialpy.saveFile(initial_file="Thumbnail Texture.png",initial_dir=config.last_used_directory, filter="*.png")
        if save_location == "":
            print("Directory wasn't chosen")
        else:
            config.last_used_directory = Path(save_location)
            thumbnail_texture.save(save_location, "png")

    @Slot()
    def export_logo_button_callback(self):
        logo_texture = self.create_logo_texture()
        if os.name == "nt":
            save_location = filedialpy.saveFile(initial_file="Logo Texture.png",filter="*.png")
        else:
            save_location = filedialpy.saveFile(initial_file="Logo Texture.png",initial_dir=config.last_used_directory,filter="*.png")
        if save_location == "":
            print("Directory wasn't chosen")
        else:
            config.last_used_directory = Path(save_location).parent
            logo_texture.save(save_location, "png")

    @Slot()
    def generate_spr_db_button_callback(self):
        spr_db = Manager()
        if os.name == "nt":
            spr_path = filedialpy.openDir(title="Choose 2d folder to generate spr_db for")
        else:
            spr_path = filedialpy.openDir(title="Choose 2d folder to generate spr_db for", initial_dir=config.last_used_directory)
        farc_list = []
        if spr_path == "":
            print("Folder wasn't chosen")
        else:
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