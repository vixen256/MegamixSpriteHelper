import io
import math
from pathlib import Path, PurePath
from typing import Callable

import PySide6
from PySide6.QtCore import Qt, QRectF, QPoint, Signal, QObject, QSize, QRect, QBuffer, QIODevice
from enum import Enum, auto, StrEnum
from PySide6.QtGui import QColor, QImage, QPixmap, QPainter, QTransform
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QGraphicsPixmapItem, QFileDialog, QGraphicsScene, QLayout, QGraphicsView
from wand.color import Color
from wand.image import Image

from widgets import EditableDoubleLabel


class ThumbnailCheck(Enum):
    FULLY_OPAQUE = [15293.325646817684]
    SPRITE_HELPER_EXPORTED = [15409.511583194137]
    SPRITE_HELPER_EXPORTED_OLD = [15403.198932036757]

class State(Enum):
    FALLBACK = auto()
    IMAGE_TOO_SMALL = auto()
    UPDATED = auto()

class SpriteType(StrEnum):
    JACKET = "Jacket"
    BACKGROUND = "Background"
    THUMBNAIL = "Thumbnail"
    LOGO = "Logo"

class SpriteSetting(StrEnum):
    HORIZONTAL_OFFSET = "Horizontal Offset"
    VERTICAL_OFFSET = "Vertical Offset"
    ROTATION = "Rotation"
    ZOOM = "Zoom"

class Scene(Enum):
    MEGAMIX_SONG_SELECT = auto()
    MEGAMIX_RESULT = auto()
    FUTURE_TONE_SONG_SELECT = auto()
    FUTURE_TONE_RESULT = auto()

####################################################
def round_up(number, decimal_places):
    factor = 10 ** decimal_places
    return math.ceil(number * factor) / factor

def _has_transparent_corners(qimage):
    width = qimage.width()
    height = qimage.height()

    corners = [
        (0, 0),  # Top-left
        (width, 0),  # Top-right
        (0, height),  # Bottom-left
        (width, height)  # Bottom-right
    ]

    for x, y in corners:
        if x < width and y < height:
            pixel = qimage.pixel(x, y)
            alpha = (pixel >> 24) & 0xFF
            if alpha == 0:
                return True

    return False
def trim_to_opaque(qimage):
    if qimage.format() != QImage.Format_RGBA8888:
        qimage = qimage.convertToFormat(QImage.Format_RGBA8888)


    needs_trim = _has_transparent_corners(qimage)

    if not needs_trim:
        return qimage

    buffer = QBuffer()
    buffer.open(QIODevice.ReadWrite)
    qimage.save(buffer, "PNG")

    with Image(blob=buffer.data().data()) as img:
        img.background_color = Color('transparent')
        img.trim()
        img.format = 'PNG'
        trimmed_data = img.make_blob()

    trimmed_qimage = QImage()
    trimmed_qimage.loadFromData(trimmed_data, 'PNG')
    return trimmed_qimage

######################################################
class QScalingGraphicsScene(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setViewport(QOpenGLWidget())
    def resizeEvent(self,event):
        self.fitInView(self.scene().sceneRect())


class QSpriteBase(QGraphicsPixmapItem, QObject):
    SpriteUpdated = Signal()
    def __init__(self,
                 sprite:Path,
                 sprite_type:SpriteType,
                 size:PySide6.QtCore.QRectF,
                 scale:float=None,
                 offset:QPoint=QPoint(0,0)):
        QObject.__init__(self)
        QGraphicsPixmapItem.__init__(self)
        #Set default image and fallback dummy.
        self.dummy_location = sprite
        self.location = sprite
        self.sprite_size = size
        self.offset=offset
        if scale:
            self.setScale(scale)

        self.sprite_image = QImage(self.location)
        self.calc_size = self.sprite_image.size()
        self.x = 0
        self.y = 0


        #Create a scene that will crop image to max size
        self.sprite = QGraphicsPixmapItem()
        self.sprite.setPixmap(QPixmap(self.sprite_image))
        self.sprite_scene = QGraphicsScene()
        self.sprite_scene.setSceneRect(self.sprite_size)
        self.sprite_scene.addItem(self.sprite)

        self.type = sprite_type


        self.sprite_settings = [
            (SpriteSetting.HORIZONTAL_OFFSET, {
                'initial_value': 0,
                'decimals': 0,
                'rough_step': 1,
                'precise_step': 1
            }),
            (SpriteSetting.VERTICAL_OFFSET, {
                'initial_value': 0,
                'decimals': 0,
                'rough_step': 1,
                'precise_step': 1
            }),
            (SpriteSetting.ROTATION, {
                'initial_value': 0,
                'decimals': 0,
                'rough_step': 1,
                'precise_step': 1
            }),
            (SpriteSetting.ZOOM, {
                'initial_value': 1,
                'decimals': 3,
                'rough_step': 0.001,
                'precise_step': 0.001
            })
        ]
        self.flipped_h = False
        self.flipped_v = False
        self.edit_controls = self.create_edit_controls()

        self.last_value = {}
        self.initial_calc = True
        self.update_sprite()
        self.edit_controls[SpriteSetting.ZOOM.value].setValue(self.edit_controls[SpriteSetting.ZOOM.value].spinbox.maximum())


    def create_edit_controls(self) -> dict[Callable[[], str], EditableDoubleLabel]:
        editable_values = {}
        for setting in self.sprite_settings:
            parameters = setting[1]
            edit = EditableDoubleLabel(sprite=self,
                                       setting=setting[0],
                                       range=self.calculate_range(setting[0]),
                                       **parameters)
            edit.editingFinished.connect(self.update_sprite)
            editable_values[setting[0].value] = edit
        return editable_values

    def add_edit_controls_to(self,layout:QLayout):
        for control in self.edit_controls:
            layout.addWidget(self.edit_controls[control])


    def grab_scene_portion(self,scene:QGraphicsScene, source_rect:QRectF) -> QPixmap:
        pixmap = QPixmap(source_rect.size().toSize())
        pixmap.fill("transparent")

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        scene.render(painter, QRectF(pixmap.rect()), source_rect)
        painter.end()

        return pixmap

    def calculate_range(self,sprite_setting:SpriteSetting):
        match sprite_setting:
            case SpriteSetting.HORIZONTAL_OFFSET:
                if self.calc_size.width() > 0:
                    offset = self.required_size().width() - self.calc_size.width()
                else:
                    offset = (self.calc_size.width() * -1) + self.required_size().width()

                if offset > 0:
                    return -offset, 0
                elif 0 > offset:
                    return offset+self.x, -self.x
                else:
                    return 0, 0

            case SpriteSetting.VERTICAL_OFFSET:
                if self.calc_size.height() > 0:
                    offset = self.required_size().height() - self.calc_size.height()
                else:
                    offset = (self.calc_size.height() * -1) + self.required_size().height()

                if offset > 0:
                    return -offset,0
                elif 0 > offset:
                    return offset-self.y, -self.y
                else:
                    return 0, 0
            case SpriteSetting.ZOOM:
                if self.required_size() == QSize(0,0):
                    return 0.10,1.00
                if self.calc_size.width() == 0:
                    return 1.00,1.00
                if self.calc_size.height() == 0:
                    return 1.00,1.00

                width_factor = self.required_size().width() / self.sprite_image.width()
                height_factor = self.required_size().height() / self.sprite_image.height()
                #TODO Round it up to number of decimals specified in sprite settings
                if width_factor > height_factor:
                    return round_up(width_factor,3), 1.00
                elif width_factor < height_factor:
                    return round_up(height_factor,3), 1.00
                else:
                    return round_up(height_factor,3), 1.00
            case SpriteSetting.ROTATION:
                return 0, 360

    def required_size(self) -> None|QSize:
        return self.sprite_size.size().toSize()

    def update_all_ranges(self):
        for setting in self.edit_controls:
            self.edit_controls[setting].set_range(self.calculate_range(setting))
    def load_new_image(self,image_location):
        #TODO - Must take inconsideration REAL area of the image - ignore transparent areas
        #           Ideally check for transparent holes in images like jacket , background

        #TODO - Should return nice error codes , states
        #       -Image.TooSmall
        #       -Image.ContainsTransparency
        #       -Success
        #       -Success.JacketFitted
        #
        #TODO - Should allow for easy per-sprite adjustments after the sprite is loaded in without replacing whole function
        #TODO - Add optional fallback to dummy sprite -Needed for watcher


        qimage = trim_to_opaque(QImage(image_location))
        required_size = self.required_size()

        if required_size:
            rw = required_size.width()
            rh = required_size.height()
            w = qimage.width()
            h = qimage.height()

            if (w, h) < (rw, rh):
                print(f"Chosen image for {self.type.value} is too small. It's size is {w,h}")
                print(f"Required size for the sprite is {rw,rh}")
                return

        self.sprite_image = qimage
        self.setPixmap(QPixmap(qimage))
        self.location = image_location
        self.initial_calc = True

        for setting in self.edit_controls:
            self.edit_controls[setting].setValue(self.edit_controls[setting].initial_value)

        self.update_sprite()

    def update_sprite(self):
        zoom = self.edit_controls[SpriteSetting.ZOOM.value].value
        horizontal_offset = self.edit_controls[SpriteSetting.HORIZONTAL_OFFSET.value].value
        vertical_offset = self.edit_controls[SpriteSetting.VERTICAL_OFFSET.value].value
        rotation = self.edit_controls[SpriteSetting.ROTATION.value].value

        result = QImage(self.sprite_size.size().toSize(), QImage.Format.Format_ARGB32)
        result.fill(Qt.transparent)
        painter = QPainter(result)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        transform = QTransform()
        transform.translate(horizontal_offset, vertical_offset)
        transform.scale(zoom, zoom)
        transform.translate((image_size.width()/2)*zoom,(image_size.height()/2)*zoom)
        transform.rotate(rotation)
        transform.translate(-(image_size.width()/2)*zoom,-(image_size.height()/2)*zoom)

        painter.setTransform(transform,combine=False)
        painter.drawPixmap(0+self.offset.x(), 0+self.offset.y(), QPixmap(self.sprite_image))
        painter.end()

        original_rect = QRectF(0+self.offset.x(), 0+self.offset.y(), self.sprite_image.width(), self.sprite_image.height())
        self.calc_size = transform.mapRect(original_rect).size().toSize()
        self.x = int(transform.mapRect(original_rect).x()) - horizontal_offset
        self.y = int(transform.mapRect(original_rect).y()) - vertical_offset

        self.sprite.setPixmap(QPixmap(result))
        self.update_pixmap()

        recalculate_offsets = False

        if self.initial_calc:
            for setting in self.edit_controls:
                self.last_value[setting] = self.edit_controls[setting].value

            self.update_all_ranges()
            self.initial_calc = False
        else:
            for setting in self.last_value:
                if self.edit_controls[setting].value != self.last_value[setting]:
                    if setting in ["Horizontal Offset" , "Vertical Offset"]:
                        continue
                    else:
                        recalculate_offsets = True
                        break

        if recalculate_offsets:
            self.update_all_ranges()
            for setting in self.edit_controls:
                self.last_value[setting] = self.edit_controls[setting].value

        self.SpriteUpdated.emit()

    def update_pixmap(self):
        self.setPixmap(self.grab_scene_portion(self.sprite_scene, self.sprite_size))

    def mousePressEvent(self, event, /):
        self.save_image()

        super().mousePressEvent(event)

    def save_image(self):
        filename, _ = QFileDialog.getSaveFileName(
            None,
            "Save Image",
            "image.png",
            "PNG Files (*.png)"
        )
        if filename:
            self.pixmap().save(filename, "PNG",100)
            print(f"Image saved to: {filename}")
class QThumbnail(QSpriteBase):
    def __init__(self,
                 sprite: Path,
                 size: PySide6.QtCore.QRectF,
                 mask: Path):

        self.sprite_mask = QImage(mask)
        super().__init__(sprite,SpriteType.THUMBNAIL,size,offset=QPoint(28,1))
        print("Loading new thumb")
        self.load_new_image(self.location)
        print(self.sprite_image.size())

        #TODO Thumbnail is ignoring it's offset when zooming out
    def required_size(self) -> QSize:
        return QSize(100,61)

    def apply_mask_to_pixmap(self, pixmap:QPixmap) -> QPixmap:
        #TODO Needs to apply mask with // Probably only for final image.
        # (Wand) magick image.png mask.png -compose CopyOpacity -composite result.png

        result_pixmap = QPixmap(self.sprite.pixmap().size())
        result_pixmap.fill("transparent")  # This prevents ghost images from showing up

        painter = QPainter(result_pixmap)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        painter.drawPixmap(0, 0, pixmap)

        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)

        painter.drawImage(0, 0, self.sprite_mask)
        painter.end()

        return result_pixmap

    def update_pixmap(self):
        self.setPixmap(self.apply_mask_to_pixmap(self.grab_scene_portion(self.sprite_scene, self.sprite_size)))

class QJacket(QSpriteBase):
    def __init__(self,sprite: Path,
                 size: PySide6.QtCore.QRectF):
        super().__init__(sprite,SpriteType.JACKET,size)

    def apply_fix(self,image:QImage) -> QImage:
        w = image.width()
        h = image.height()
        image_s = image

        image_fix = QImage(QSize(502,502), QImage.Format_ARGB32)
        image_fix.fill(Qt.transparent)

        painter = QPainter(image_fix)
        painter.setOpacity(144/255)
        painter.drawImage(0,0,image_s.scaled(w+2, h+2))
        painter.setOpacity(255)
        painter.drawImage(1,1,image)
        painter.end()

        return image_fix

    def required_size(self) -> QSize:
        return QSize(500,500)

    def update_pixmap(self):
        self.setPixmap(QPixmap(self.apply_fix(self.grab_scene_portion(self.sprite_scene,self.sprite_size).toImage())))

class QBackground(QSpriteBase):
    def __init__(self,sprite,size):
        super().__init__(sprite,SpriteType.BACKGROUND,size)

    def required_size(self) -> QSize:
        return QSize(1280,720)

class QLogo(QSpriteBase):
    def __init__(self,sprite,size):
        super().__init__(sprite,SpriteType.LOGO,size)
    def required_size(self) -> QSize:
        return QSize(0,0)



class QSpriteSlave(QGraphicsPixmapItem):

    def __init__(self, tracked: QSpriteBase, position: QPoint,scale:float=None,rotation:int=None):
        super().__init__()
        self.tracked = tracked
        tracked.SpriteUpdated.connect(self.update_sprite)
        self.rotation = rotation
        self.scale = scale
        self.setPos(position)
        self.setTransformationMode(Qt.SmoothTransformation)

        self.update_sprite()
    def update_sprite(self):
        #TODO It gets scaled wrong when image has transparency as it doesn't get included in calc
        if self.scale:
            self.setPixmap(self.tracked.pixmap())
            self.setScale(self.scale)
        else:
            self.setPixmap(self.tracked.pixmap())

        if self.rotation:
            image = self.pixmap().toImage()
            image = image.transformed(QTransform().rotate(self.rotation))
            self.setPixmap(QPixmap(image))

class QLayer(QGraphicsPixmapItem):
    def __init__(self,
                 sprite: Path,
                 size: PySide6.QtCore.QRectF = QRectF(0,0,1920,1080),
                 scale:float=1):
        super().__init__()
        self.sprite_size = size
        self.setPixmap(QPixmap(QImage(sprite)))
        self.setTransformationMode(Qt.SmoothTransformation)
        self.setScale(scale)

class QControllableSprites:
    def __init__(self):
        self.thumbnail = QThumbnail(Path(Path.cwd() / "Images/Dummy/SONG_JK_THUMBNAIL_DUMMY.png"),
                                      QRectF(0, 0, 128, 64),
                                      Path(Path.cwd() / "Images/Dummy/Thumbnail-Maskv3.png"))

        self.logo = QLogo(Path(Path.cwd() / "Images/Dummy/SONG_LOGO_DUMMY.png"),
                            QRectF(0, 0, 870, 330))
        self.jacket = QJacket(Path(Path.cwd() / 'Images/Dummy/SONG_JK_DUMMY.png'),
                                QRectF(0, 0, 502, 502))
        self.background = QSpriteBase(Path(Path.cwd() / 'Images/Dummy/SONG_BG_DUMMY.png'),
                                        SpriteType.BACKGROUND,
                                        QRectF(0, 0, 1280, 720))

class QMMSongSelectScene(QGraphicsScene):
    def __init__(self,jacket:QJacket, logo:QLogo, background:QSpriteBase, thumbnail:QThumbnail):
        super().__init__()

        #####
        self.jacket = QSpriteSlave(jacket, QPoint(1284, 130), rotation=7)
        self.logo = QSpriteSlave(logo, QPoint(825, 537), scale=0.8)
        self.background = QSpriteSlave(background,QPoint(0,0), scale=1.50)
        self.thumbnail_1 = QSpriteSlave(thumbnail, QPoint(-98, -24), scale=1.25)
        self.thumbnail_2 = QSpriteSlave(thumbnail, QPoint(-66, 90), scale=1.25)
        self.thumbnail_3 = QSpriteSlave(thumbnail, QPoint(-34, 204), scale=1.25)
        self.thumbnail_selected = QSpriteSlave(thumbnail, QPoint(-8, 332), scale=1.578125)
        self.thumbnail_4 = QSpriteSlave(thumbnail, QPoint(44, 476), scale=1.25)
        self.thumbnail_5 = QSpriteSlave(thumbnail, QPoint(108, 704), scale=1.25)
        self.thumbnail_6 = QSpriteSlave(thumbnail, QPoint(140, 818), scale=1.25)
        self.thumbnail_7 = QSpriteSlave(thumbnail, QPoint(168, 948), scale=1.25)
        ######
        self.backdrop = QLayer(Path.cwd() / 'Images/MM UI - Song Select/Backdrop.png')
        self.song_selector = QLayer(Path.cwd() / 'Images/MM UI - Song Select/Song Selector.png')
        self.middle_layer = QLayer(Path.cwd() / 'Images/MM UI - Song Select/Middle Layer.png')
        self.top_layer_new_classics = QLayer(Path.cwd() / 'Images/MM UI - Song Select/Top Layer - New Classics.png')
        self.top_layer = QLayer(Path.cwd() / 'Images/MM UI - Song Select/Top Layer.png')
        ######
        self.setSceneRect(0, 0, 1920, 1080)
        self.setBackgroundBrush(Qt.black) #TODO , make it grab color of background app.

        self.addItem(self.backdrop)
        self.addItem(self.background)
        self.addItem(self.jacket)
        self.addItem(self.middle_layer)
        self.addItem(self.logo)
        self.addItem(self.song_selector)
        self.addItem(self.thumbnail_1)
        self.addItem(self.thumbnail_2)
        self.addItem(self.thumbnail_3)
        self.addItem(self.thumbnail_selected)
        self.addItem(self.thumbnail_4)
        self.addItem(self.thumbnail_5)
        self.addItem(self.thumbnail_6)
        self.addItem(self.thumbnail_7)
        self.addItem(self.top_layer_new_classics)
class QFTSongSelectScene(QGraphicsScene):
    def __init__(self,jacket:QJacket, logo:QLogo, background:QSpriteBase):
        super().__init__()
        #####
        self.jacket = QSpriteSlave(jacket, QPoint(1331, 205), rotation=-5 ,scale=0.97)
        self.logo = QSpriteSlave(logo, QPoint(803, 515), scale=0.9)
        self.background = QSpriteSlave(background,QPoint(0,0), scale=1.50)

        ######
        self.backdrop = QLayer(Path.cwd() / 'Images/FT UI - Song Select/Base.png')
        self.middle_layer = QLayer(Path.cwd() / 'Images/FT UI - Song Select/Middle Layer.png')
        self.top_layer_new_classics = QLayer(Path.cwd() / 'Images/FT UI - Song Select/Top Layer - New Classics.png')
        self.top_layer = QLayer(Path.cwd() / 'Images/FT UI - Song Select/Top Layer.png')
        ######
        self.setSceneRect(0, 0, 1920, 1080)
        self.setBackgroundBrush(Qt.black) #TODO , make it grab color of background app.

        self.addItem(self.backdrop)
        self.addItem(self.background)
        self.addItem(self.middle_layer)
        self.addItem(self.jacket)
        self.addItem(self.logo)
        self.addItem(self.top_layer_new_classics)

class QMMResultScene(QGraphicsScene):
    def __init__(self,jacket:QJacket, logo:QLogo, background:QSpriteBase):
        super().__init__()

        #####
        self.jacket = QSpriteSlave(jacket, QPoint(108, 387), rotation=7, scale=0.9)
        self.logo = QSpriteSlave(logo, QPoint(67, 784), scale=0.7)
        self.background = QSpriteSlave(background,QPoint(0,0), scale=1.50)
        ######
        self.backdrop = QLayer(Path.cwd() / 'Images/Dummy/SONG_BG_DUMMY.png',scale=1.5)
        self.middle_layer = QLayer(Path.cwd() / 'Images/MM UI - Results Screen/Middle Layer.png')
        self.top_layer_new_classics = QLayer(Path.cwd() / 'Images/MM UI - Results Screen/Top Layer - New Classics.png')
        self.top_layer = QLayer(Path.cwd() / 'Images/MM UI - Results Screen/Top Layer.png')
        ######
        self.setSceneRect(0, 0, 1920, 1080)
        self.setBackgroundBrush(Qt.black) #TODO , make it grab color of background app.

        self.addItem(self.backdrop)
        self.addItem(self.background)
        self.addItem(self.middle_layer)
        self.addItem(self.jacket)
        self.addItem(self.logo)
        self.addItem(self.top_layer_new_classics)
class QFTResultScene(QGraphicsScene):
    def __init__(self,jacket:QJacket, logo:QLogo):
        super().__init__()

        #####
        self.jacket = QSpriteSlave(jacket, QPoint(164, 303), rotation=-5)
        self.logo = QSpriteSlave(logo, QPoint(134, 663), scale=0.75)
        ######
        self.backdrop = QLayer(Path.cwd() / 'Images/FT UI - Results Screen/Base.png')
        self.middle_layer = QLayer(Path.cwd() / 'Images/FT UI - Results Screen/Middle Layer.png')
        self.top_layer_new_classics = QLayer(Path.cwd() / 'Images/FT UI - Results Screen/Top Layer - New Classics.png')
        self.top_layer = QLayer(Path.cwd() / 'Images/FT UI - Results Screen/Top Layer.png')
        ######
        self.setSceneRect(0, 0, 1920, 1080)
        self.setBackgroundBrush(Qt.black) #TODO , make it grab color of background app.

        self.addItem(self.backdrop)
        self.addItem(self.middle_layer)
        self.addItem(self.jacket)
        self.addItem(self.logo)
        self.addItem(self.top_layer_new_classics)