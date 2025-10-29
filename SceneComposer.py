import io
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path, PurePath
from typing import Callable

import PySide6
from PIL.ImageQt import QBuffer
from PySide6.QtCore import Qt, QByteArray, QIODevice, QRectF
from enum import Enum, auto, StrEnum
from PIL import Image, ImageOps, ImageQt, ImageStat, ImageShow
from PIL.Image import Resampling
from PySide6.QtGui import QColor, QImage, QPixmap, QPainter, QTransform
from PySide6.QtWidgets import QGraphicsPixmapItem, QFileDialog, QGraphicsScene, QLayout

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


def texture_filtering_fix(image, opacity):
    # Very edges of the sprite should have like 40% opacity. This makes jackets appear smooth in-game.
    t_edge = Image.new(image.mode, (image.size[0], image.size[1]))
    t_edge.alpha_composite(image)
    t_edge = t_edge.resize((image.size[0] + 2, image.size[1] + 2))
    r, g, b, a = t_edge.split()
    a = a.point(lambda x: opacity if x > 0 else 0)  # Set 102 opacity, that is 40% from 256. For Background 100% is recommended
    t_edge = Image.merge(image.mode, (r, g, b, a))
    t_edge.alpha_composite(image, (1, 1))
    return t_edge

class Sprite:
    def __init__(self,sprite_type,image_location):
        self.script_directory = Path.cwd()
        self.type = sprite_type
        self.location = image_location
        self.dummy_location = image_location
        self.sprite_settings = [
            (SpriteSetting.HORIZONTAL_OFFSET,{
                'initial_value':0,
                'decimals':0,
                'rough_step':1,
                'precise_step':1
            }),
            (SpriteSetting.VERTICAL_OFFSET,{
                'initial_value':0,
                'decimals':0,
                'rough_step':1,
                'precise_step':1
            }),
            (SpriteSetting.ROTATION,{
                'initial_value':0,
                'decimals':2,
                'rough_step':1,
                'precise_step':0.01
            }),
            (SpriteSetting.ZOOM,{
                'initial_value':1,
                'decimals':3,
                'rough_step':0.001,
                'precise_step':0.001
            })
        ]
        self.flipped_h = False
        self.flipped_v = False
        with Image.open(self.location) as open_image:
            left, upper, right, lower = open_image.getbbox()
            self.edges = (left, upper, right, lower)
            self.size = open_image.size

class BackgroundSprite(Sprite):
    def __init__(self, sprite_type, image_location):

        super().__init__(sprite_type, image_location)
        self.post_process(0,0,0,1)

    def update_sprite(self,new_location,fallback = True):
        with Image.open(new_location) as new_image:
            new_left, new_upper, new_right, new_lower = new_image.getbbox()
            new_real_width = new_right - new_left
            new_real_height = new_lower - new_upper

            if new_real_width < 1280 or new_real_height < 720:

                if fallback:
                    with Image.open(self.script_directory / 'Images/Dummy/SONG_BG_DUMMY.png') as dummy_image:
                        new_left, new_upper, new_right, new_lower = dummy_image.getbbox()
                        self.location = self.script_directory / 'Images/Dummy/SONG_BG_DUMMY.png'
                        self.edges = (new_left, new_upper, new_right, new_lower)
                        self.size = dummy_image.size
                        self.flipped_h = False
                        self.flipped_v = False

                        state = {
                            "Outcome": State.FALLBACK
                        }
                        return state
                else:

                    state = {
                        "Outcome": State.IMAGE_TOO_SMALL,
                        "Window Title": f"{self.type} image is too small",
                        "Description": f"{self.type} is too small. Image needs to be at least 1280x720.\nThis doesn't include fully transparent area"
                    }
                    return state
            else:
                self.location = new_location
                self.edges = (new_left, new_upper, new_right, new_lower)
                self.size = new_image.size

                state = {
                    "Outcome": State.UPDATED
                }
                return state

    def post_process(self,horizontal_offset,vertical_offset,rotation,zoom):
        with Image.open(self.location).convert('RGBA') as background:
            cropped_background = Image.Image.crop(background, Image.Image.getbbox(background))

            if self.flipped_h:
                cropped_background = cropped_background.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            if self.flipped_v:
                cropped_background = cropped_background.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

            self.background_image = ImageOps.scale(cropped_background.rotate(rotation, Resampling.BILINEAR, expand=True), zoom)
            self.background = Image.new('RGBA', (1280, 720))
            self.background.alpha_composite(self.background_image, (horizontal_offset, vertical_offset))
            self.scaled_background = ImageOps.scale(self.background, 1.5)

    def calculate_range(self, SpriteSetting):
        match SpriteSetting:
            case SpriteSetting.HORIZONTAL_OFFSET:
                offset = (self.background_image.width * -1) + 1280

                if offset > 0:
                    return 0,offset
                else:
                    return offset,0

            case SpriteSetting.VERTICAL_OFFSET:
                offset = (self.background_image.height * -1) + 720

                if offset > 0:
                    return 0, offset
                else:
                    return offset, 0

            case SpriteSetting.ZOOM:
                width_factor = Decimal(1280 / self.background_image.width)
                height_factor = Decimal(720 / self.background_image.width)

                if width_factor > height_factor:
                    return float(width_factor.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)), 1.00
                elif height_factor > width_factor:
                    return float(height_factor.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)), 1.00
                else:
                    return 1.00, 1.00

            case SpriteSetting.ROTATION:
                return 0,360
class JacketSprite(Sprite):
    def __init__(self, sprite_type, image_location):

        super().__init__(sprite_type, image_location)
        self.post_process(0, 0, 0, 1)
    def update_sprite(self,new_location,fallback = True):
        with Image.open(new_location) as new_image:
            new_left, new_upper, new_right, new_lower = new_image.getbbox()
            new_real_width = new_right - new_left
            new_real_height = new_lower - new_upper

        if new_real_width < 500 or new_real_height < 500:

            if fallback:
                with Image.open(self.script_directory / 'Images/Dummy/SONG_JK_DUMMY.png') as dummy_image:
                    new_left, new_upper, new_right, new_lower = dummy_image.getbbox()
                    self.location = self.script_directory / 'Images/Dummy/SONG_JK_DUMMY.png'
                    self.edges = (new_left, new_upper, new_right, new_lower)
                    self.size = dummy_image.size
                    self.flipped_h = False
                    self.flipped_v = False

                    state = {
                        "Outcome": State.FALLBACK
                    }
                    return state
            else:

                state = {
                    "Outcome": State.IMAGE_TOO_SMALL,
                    "Window Title": f"{self.type} image is too small",
                    "Description": f"{self.type} is too small. Image needs to be at least 500x500.\nThis doesn't include fully transparent area"
                }
                return state
        else:
            self.location = new_location
            self.edges = (new_left, new_upper, new_right, new_lower)
            self.size = new_image.size

            if new_real_width == new_real_height:
                zoom = 500 / new_real_width

                state = {
                    "Outcome": State.UPDATED,
                    "Jacket Force Fit": True,
                    "Zoom": zoom
                }
                return state
            else:

                state = {
                    "Outcome": State.UPDATED,
                    "Jacket Force Fit": False
                }
                return state

    def post_process(self,horizontal_offset,vertical_offset,rotation,zoom):
        with Image.open(self.location).convert('RGBA') as jacket:
            cropped_jacket = Image.Image.crop(jacket, Image.Image.getbbox(jacket))

            if self.flipped_h:
                cropped_jacket = cropped_jacket.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            if self.flipped_v:
                cropped_jacket = cropped_jacket.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

            self.jacket = Image.new('RGBA', (500, 500))
            self.jacket_image = ImageOps.scale(cropped_jacket.rotate(rotation, Resampling.BILINEAR, expand=True), zoom)
            self.jacket.alpha_composite(self.jacket_image, (horizontal_offset, vertical_offset))
            self.jacket_test = self.jacket
            self.jacket = texture_filtering_fix(self.jacket, 102)
    def calculate_range(self, SpriteSetting):
        match SpriteSetting:
            case SpriteSetting.HORIZONTAL_OFFSET:
                offset = (self.jacket_image.width * -1) + 500

                if offset > 0:
                    return 0,offset
                else:
                    return offset,0

            case SpriteSetting.VERTICAL_OFFSET:
                offset = (self.jacket_image.height * -1) + 500

                if offset > 0:
                    return 0,offset
                else:
                    return offset,0

            case SpriteSetting.ZOOM:
                width_factor = Decimal(500 / self.jacket_image.width)
                height_factor = Decimal(500 / self.jacket_image.height)

                if width_factor > height_factor:
                    return float(width_factor.quantize(Decimal('0.001'),rounding=ROUND_HALF_UP)),1.00
                elif height_factor > width_factor:
                    return float(height_factor.quantize(Decimal('0.001'),rounding=ROUND_HALF_UP)),1.00
                else:
                    return 1.00,1.00
            case SpriteSetting.ROTATION:
                return 0,360


class LogoSprite(Sprite):
    def __init__(self, sprite_type, image_location):

        super().__init__(sprite_type, image_location)
        self.post_process(Qt.CheckState.Checked,0, 0, 0, 1)
    def update_sprite(self,new_location,fallback = True):
        with Image.open(new_location) as new_image:
            new_left, new_upper, new_right, new_lower = new_image.getbbox()

            self.location = new_location
            self.edges = (new_left, new_upper, new_right, new_lower)
            self.size = new_image.size

            state = {
                "Outcome": State.UPDATED
            }
            return state

    def post_process(self,state,horizontal_offset,vertical_offset,rotation,zoom):
        if state == Qt.CheckState.Checked:
            with Image.open(self.location).convert('RGBA') as logo:
                if self.flipped_h:
                    logo = logo.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                if self.flipped_v:
                    logo = logo.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

                self.logo_image = ImageOps.scale(logo.rotate(rotation, Resampling.BILINEAR, expand=True), zoom)
                self.logo = Image.new('RGBA', (870, 330))
                self.logo.alpha_composite(self.logo_image, (horizontal_offset, vertical_offset))
        else:
            self.logo = Image.new('RGBA', (870, 330))

    def calculate_range(self,SpriteSetting):
        match SpriteSetting:
            case SpriteSetting.HORIZONTAL_OFFSET:
                with self.logo_image as logo:
                    left, upper, right, lower = Image.Image.getbbox(logo)

                    offset = 870 - right

                    if offset > -left:
                        return -left, offset
                    else:
                        return offset, -left

            case SpriteSetting.VERTICAL_OFFSET:
                with self.logo_image as logo:
                    left, upper, right, lower = Image.Image.getbbox(logo)

                    offset = 330 - lower

                    if offset > -upper:
                        return -upper, offset
                    else:
                        return offset, -upper
            case SpriteSetting.ZOOM:
                with self.logo_image as logo:
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

                return 0, max_scale
            case SpriteSetting.ROTATION:
                return 0,360

class ThumbnailSprite(Sprite):
    def __init__(self, sprite_type, image_location):

        super().__init__(sprite_type, image_location)
        self.post_process(0, 0, 0, 1)
    def update_sprite(self,new_location,fallback = True):
        with Image.open(new_location) as new_image:
            new_left, new_upper, new_right, new_lower = new_image.getbbox()
            new_real_width = new_right - new_left
            new_real_height = new_lower - new_upper

            if new_real_width < 100 or new_real_height < 61:

                if fallback:
                    with Image.open(self.script_directory / 'Images/Dummy/SONG_JK_THUMBNAIL_DUMMY.png') as dummy_image:
                        new_left, new_upper, new_right, new_lower = dummy_image.getbbox()
                        self.location = self.script_directory / 'Images/Dummy/SONG_JK_THUMBNAIL_DUMMY.png'
                        self.edges = (new_left, new_upper, new_right, new_lower)
                        self.size = dummy_image.size
                        self.flipped_h = False
                        self.flipped_v = False

                        state = {
                            "Outcome": State.FALLBACK
                        }
                        return state
                else:

                    state = {
                        "Outcome": State.IMAGE_TOO_SMALL,
                        "Window Title": f"{self.type} image is too small",
                        "Description": f"{self.type} is too small. Image needs to be at least 100x61.\nThis doesn't include fully transparent area"
                    }
                    return state
            else:
                self.location = new_location
                self.edges = (new_left, new_upper, new_right, new_lower)
                self.size = new_image.size

                state = {
                    "Outcome": State.UPDATED
                }
                return state

    def post_process(self,horizontal_offset,vertical_offset,rotation,zoom):
        with Image.open(self.location).convert('RGBA') as thumbnail, Image.open(self.script_directory / 'Images/Dummy/Thumbnail-Maskv2.png').convert('L') as mask:
            cropped_thumbnail = Image.Image.crop(thumbnail, Image.Image.getbbox(thumbnail))

            if self.flipped_h:
                cropped_thumbnail = cropped_thumbnail.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            if self.flipped_v:
                cropped_thumbnail = cropped_thumbnail.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

            self.uncropped_thumbnail_image = ImageOps.scale(thumbnail.rotate(rotation, Resampling.BILINEAR, expand=True), zoom)

            self.thumbnail_image = ImageOps.scale(cropped_thumbnail.rotate(rotation, Resampling.BILINEAR, expand=True), zoom)
            self.thumbnail = Image.new('RGBA', (128, 64))
            self.thumbnail.alpha_composite(self.thumbnail_image, (horizontal_offset + 28, vertical_offset + 1))
            self.thumbnail_test = Image.composite(self.thumbnail,Image.new('RGBA',(128,64)),mask) #This doesn't fill in transparent area with black. Used only to get info what pixels are filled in.
            self.thumbnail.putalpha(mask) #Used for final image, forces exact same transparency as mask.
    def calculate_range(self,SpriteSetting):
        match SpriteSetting:
            case SpriteSetting.HORIZONTAL_OFFSET:
                offset = (self.thumbnail_image.width * -1) + 100

                if offset > 0:
                    return 0, offset
                else:
                    return offset, 0

            case SpriteSetting.VERTICAL_OFFSET:
                offset = (self.thumbnail_image.height * -1) + 61

                if offset > 0:
                    return 0, offset
                else:
                    return offset, 0
            case SpriteSetting.ZOOM:
                width_factor = Decimal(100 / self.thumbnail_image.width)
                height_factor = Decimal(61 / self.thumbnail_image.height)

                if width_factor > height_factor:
                    return float(width_factor.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)), 1.00
                elif width_factor < height_factor:
                    return float(height_factor.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)), 1.00
                else:
                    return 1.00, 1.00
            case SpriteSetting.ROTATION:
                return 0,360
class SceneBase:
    def __init__(self,*args):
        self.layers = ()
        self.sprites = []
        for arg in args:
            self.sprites.append(arg)

    def draw_scene(self):
        composite = Image.new('RGBA', (1920, 1080))
        for layer in self.layers:
            sprite, position = layer[0], layer[1]
            composite.alpha_composite(sprite, position)
        return composite

class MegamixSongSelect(SceneBase):
    def __init__(self,background,logo,thumbnail,jacket):
        super().__init__(background,logo,thumbnail,jacket)
        self.shared_background = background
        self.shared_logo = logo
        self.shared_thumbnail = thumbnail
        self.shared_jacket = jacket

        # Load images needed
        self.backdrop = Image.open(Path.cwd() / 'Images/MM UI - Song Select/Backdrop.png').convert('RGBA')
        self.song_selector = Image.open(Path.cwd() / 'Images/MM UI - Song Select/Song Selector.png').convert('RGBA')
        self.middle_layer = Image.open(Path.cwd() / 'Images/MM UI - Song Select/Middle Layer.png').convert('RGBA')

        self.top_layer_new_classics = Image.open(Path.cwd() / 'Images/MM UI - Song Select/Top Layer - New Classics.png').convert('RGBA')
        self.top_layer = Image.open(Path.cwd() / 'Images/MM UI - Song Select/Top Layer.png').convert('RGBA')

        self.top_layer_used = self.top_layer_new_classics

        self.jacket_anchor_point = (1284, 130)
        self.jacket_angle = -7

        self.logo_anchor_point = (825, 537)
        self.logo_scale = 0.8

        self.thumbnail_size =  (160, 76)
        self.selected_thumbnail_size = (202, 98)

        self.thumbnail_1_anchor_point = (-98, -24)
        self.thumbnail_2_anchor_point = (-66, 90)
        self.thumbnail_3_anchor_point = (-34, 204)
        self.selected_thumbnail_anchor_point = (-8, 332)
        self.thumbnail_4_anchor_point = (44, 476)
        self.thumbnail_5_anchor_point = (108, 704)
        self.thumbnail_6_anchor_point = (140, 818)
        self.thumbnail_7_anchor_point = (168, 943)

        self.prepare_sprites()
        self.reload_layers()

    def reload_layers(self):
        self.layers = (
            (self.backdrop, (0, 0)),
            (self.shared_background.scaled_background, (0, 0)),
            (self.rotated_jacket, self.jacket_anchor_point),
            (self.middle_layer, (0, 0)),
            (self.scaled_logo, self.logo_anchor_point),
            (self.song_selector, (0, 0)),
            (self.resized_thumbnail, self.thumbnail_1_anchor_point),
            (self.resized_thumbnail, self.thumbnail_2_anchor_point),
            (self.resized_thumbnail, self.thumbnail_3_anchor_point),
            (self.resized_selected_thumbnail, self.selected_thumbnail_anchor_point),
            (self.resized_thumbnail, self.thumbnail_4_anchor_point),
            (self.resized_thumbnail, self.thumbnail_5_anchor_point),
            (self.resized_thumbnail, self.thumbnail_6_anchor_point),
            (self.resized_thumbnail, self.thumbnail_7_anchor_point),
            (self.top_layer_used, (0, 0))
        )
    def prepare_sprites(self):
        self.rotated_jacket = self.shared_jacket.jacket.rotate(self.jacket_angle, Resampling.BILINEAR, expand=True)
        self.scaled_logo = ImageOps.scale(self.shared_logo.logo, self.logo_scale)
        self.resized_thumbnail = self.shared_thumbnail.thumbnail.resize(self.thumbnail_size, resample=Resampling.BILINEAR)
        self.resized_selected_thumbnail = self.shared_thumbnail.thumbnail.resize(self.selected_thumbnail_size, resample=Resampling.BILINEAR)

    def compose_scene(self,new_classics_state):
        self.prepare_sprites()

        if new_classics_state:
            self.top_layer_used = self.top_layer_new_classics
        else:
            self.top_layer_used = self.top_layer

        self.reload_layers()

        drawn_scene = self.draw_scene()
        return drawn_scene
class MegamixResult(SceneBase):
    def __init__(self,background,logo,jacket):
        super().__init__(background,logo,jacket)
        self.shared_background = background
        self.shared_logo = logo
        self.shared_jacket = jacket

        # Load images needed
        self.backdrop = ImageOps.scale(Image.open((Path.cwd() / 'Images/Dummy/SONG_BG_DUMMY.png')), 1.5)
        self.middle_layer = Image.open((Path.cwd() / 'Images/MM UI - Results Screen/Middle Layer.png'))
        self.top_layer_new_classics = Image.open((Path.cwd() / 'Images/MM UI - Results Screen/Top Layer - New Classics.png'))
        self.top_layer = Image.open((Path.cwd() / 'Images/MM UI - Results Screen/Top Layer.png'))

        self.top_layer_used = self.top_layer_new_classics

        self.mm_result_jacket_angle = -7
        self.mm_result_jacket_scale = 0.9
        self.mm_result_logo_scale = 0.7

        self.mm_result_jacket_anchor_point = (108, 387)
        self.mm_result_logo_anchor_point = (67, 784)

        self.prepare_sprites()
        self.reload_layers()

    def reload_layers(self):
        self.layers = (
                    (self.backdrop,(0,0)),
                    (self.shared_background.scaled_background,(0,0)),
                    (self.middle_layer,(0,0)),
                    (self.rotated_jacket,self.mm_result_jacket_anchor_point),
                    (self.scaled_logo,self.mm_result_logo_anchor_point),
                    (self.top_layer_used,(0,0))
                )
    def prepare_sprites(self):
        scaled_jacket = ImageOps.scale(self.shared_jacket.jacket, self.mm_result_jacket_scale)
        self.rotated_jacket = scaled_jacket.rotate(self.mm_result_jacket_angle, Resampling.BILINEAR, expand=True)
        self.scaled_logo = ImageOps.scale(self.shared_logo.logo, self.mm_result_logo_scale)

    def compose_scene(self,new_classics_state):
        self.prepare_sprites()

        if new_classics_state:
            self.top_layer_used = self.top_layer_new_classics
        else:
            self.top_layer_used = self.top_layer

        self.reload_layers()

        drawn_scene = self.draw_scene()
        return drawn_scene
class FutureToneSongSelect(SceneBase):
    def __init__(self,background,logo,jacket):
        super().__init__(background,logo,jacket)
        self.shared_background = background
        self.shared_logo = logo
        self.shared_jacket = jacket

        # Load images needed
        self.backdrop = Image.open((Path.cwd() / 'Images/FT UI - Song Select/Base.png'))
        self.middle_layer = Image.open((Path.cwd() / 'Images/FT UI - Song Select/Middle Layer.png'))
        self.top_layer_new_classics = Image.open((Path.cwd() / 'Images/FT UI - Song Select/Top Layer - New Classics.png'))
        self.top_layer = Image.open((Path.cwd() / 'Images/FT UI - Song Select/Top Layer.png'))
        self.top_layer_used = self.top_layer_new_classics

        self.ft_song_selector_jacket_scale = 0.97
        self.ft_song_selector_jacket_angle = 5
        self.ft_song_selector_logo_scale = 0.9

        self.ft_song_selector_jacket_anchor_point = (1331, 205)
        self.ft_song_selector_logo_anchor_point = (803, 515)

        self.prepare_sprites()
        self.reload_layers()

    def reload_layers(self):
        self.layers = (
                    (self.backdrop,(0,0)),
                    (self.shared_background.scaled_background,(0,0)),
                    (self.middle_layer,(0,0)),
                    (self.rotated_jacket,self.ft_song_selector_jacket_anchor_point),
                    (self.scaled_logo,self.ft_song_selector_logo_anchor_point),
                    (self.top_layer_used,(0,0))
                )
    def prepare_sprites(self):
        scaled_jacket = ImageOps.scale(self.shared_jacket.jacket, self.ft_song_selector_jacket_scale)
        self.rotated_jacket = scaled_jacket.rotate(self.ft_song_selector_jacket_angle, Resampling.BILINEAR, expand=True)
        self.scaled_logo = ImageOps.scale(self.shared_logo.logo, self.ft_song_selector_logo_scale)
    def compose_scene(self,new_classics_state):
        self.prepare_sprites()

        if new_classics_state:
            self.top_layer_used = self.top_layer_new_classics
        else:
            self.top_layer_used = self.top_layer

        self.reload_layers()

        drawn_scene = self.draw_scene()
        return drawn_scene
class FutureToneResult(SceneBase):
    def __init__(self,logo,jacket):
        super().__init__(logo,jacket)
        self.shared_logo = logo
        self.shared_jacket = jacket

        #Load images needed
        self.backdrop = Image.open((Path.cwd() / 'Images/FT UI - Results Screen/Base.png'))
        self.middle_layer = Image.open((Path.cwd() / 'Images/FT UI - Results Screen/Middle Layer.png'))
        self.top_layer_new_classics = Image.open((Path.cwd() / 'Images/FT UI - Results Screen/Top Layer - New Classics.png'))
        self.top_layer = Image.open((Path.cwd() / 'Images/FT UI - Results Screen/Top Layer.png'))
        self.top_layer_used = self.top_layer_new_classics

        self.ft_result_jacket_anchor_point = (164, 303)
        self.ft_result_jacket_angle = 5
        self.ft_result_logo_anchor_point = (134, 663)
        self.ft_result_logo_scale = 0.75

        self.prepare_sprites()
        self.reload_layers()

    def reload_layers(self):
        self.layers = (
                    (self.backdrop,(0,0)),
                    (self.middle_layer,(0,0)),
                    (self.rotated_jacket,self.ft_result_jacket_anchor_point),
                    (self.scaled_logo,self.ft_result_logo_anchor_point),
                    (self.top_layer_used,(0,0))
                )

    def prepare_sprites(self):
        self.rotated_jacket = self.shared_jacket.jacket.rotate(self.ft_result_jacket_angle, Resampling.BILINEAR, expand=True)
        self.scaled_logo = ImageOps.scale(self.shared_logo.logo, self.ft_result_logo_scale)

    def compose_scene(self,new_classics_state):
        self.prepare_sprites()

        if new_classics_state:
            self.top_layer_used = self.top_layer_new_classics
        else:
            self.top_layer_used = self.top_layer

        self.reload_layers()

        drawn_scene = self.draw_scene()
        return drawn_scene

class SceneComposer:

    def __init__(self):
        self.loaded_scenes = []
        #Create objects storing information about images
        self.Background = BackgroundSprite(SpriteType.BACKGROUND,Path.cwd() / 'Images/Dummy/SONG_BG_DUMMY.png')
        self.Jacket = JacketSprite(SpriteType.JACKET, Path.cwd() / 'Images/Dummy/SONG_JK_DUMMY.png')
        self.Logo = LogoSprite(SpriteType.LOGO, Path.cwd() / 'Images/Dummy/SONG_LOGO_DUMMY.png')
        self.Thumbnail = ThumbnailSprite(SpriteType.THUMBNAIL, Path.cwd() / 'Images/Dummy/SONG_JK_THUMBNAIL_DUMMY.png')

        self.Megamix_Song_Select = MegamixSongSelect(self.Background,self.Logo,self.Thumbnail,self.Jacket)
        self.Megamix_Result = MegamixResult(self.Background,self.Logo,self.Jacket)
        self.FutureTone_Song_Select = FutureToneSongSelect(self.Background,self.Logo,self.Jacket)
        self.FutureTone_Result = FutureToneResult(self.Logo,self.Jacket)

        self.loaded_scenes.append(self.Megamix_Song_Select)
        self.loaded_scenes.append(self.Megamix_Result)
        self.loaded_scenes.append(self.FutureTone_Song_Select)
        self.loaded_scenes.append(self.FutureTone_Result)

    def get_required_sprites(self):
        sprite_list = []
        for loaded_scene in self.loaded_scenes:
            for sprite in loaded_scene.sprites:
                if sprite in sprite_list:
                    pass
                else:
                    sprite_list.append(sprite)

        return sprite_list

    def check_sprite(self,sprite):
        match sprite:
            case SpriteType.JACKET:
                if ImageStat.Stat(self.Jacket.jacket_test).extrema[3] == (255,255):
                    return True
                else:
                    return False
            case SpriteType.BACKGROUND:
                if ImageStat.Stat(self.Background.scaled_background).extrema[3] == (255,255):
                    return True
                else:
                    return False
            case SpriteType.THUMBNAIL:
                thumbnail_area_covered = ImageStat.Stat(self.Thumbnail.thumbnail_test.getchannel("A")).var
                if thumbnail_area_covered in ThumbnailCheck:
                    return True
                else:
                    return False

####################################################
class QSpriteBase(QGraphicsPixmapItem):
    def __init__(self,
                 sprite:Path,
                 sprite_type:SpriteType,
                 size:PySide6.QtCore.QRectF):
        super().__init__()
        #Set default image and fallback dummy.
        self.dummy_location = sprite
        self.location = sprite
        self.sprite_size = size

        self.sprite_image = QImage(self.location)

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
                'decimals': 2,
                'rough_step': 1,
                'precise_step': 0.01
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

        self.update_sprite()

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
        #painter.setRenderHint(QPainter.LosslessImageRendering)
        scene.render(painter, QRectF(pixmap.rect()), source_rect)
        painter.end()

        return pixmap

    def calculate_range(self,sprite_setting:SpriteSetting):
        match sprite_setting:
            case SpriteSetting.HORIZONTAL_OFFSET:
                offset = (self.sprite_image.width() * -1) + self.sprite_scene.width()

                if offset > 0:
                    return 0, offset
                else:
                    return offset, 0

            case SpriteSetting.VERTICAL_OFFSET:
                offset = (self.sprite_image.height() * -1) + self.sprite_scene.height()

                if offset > 0:
                    return 0, offset
                else:
                    return offset, 0
            case SpriteSetting.ZOOM:
                width_factor = Decimal(self.sprite_scene.width() / self.sprite_image.width())
                height_factor = Decimal(self.sprite_scene.height() / self.sprite_image.height())

                if width_factor > height_factor:
                    return float(width_factor.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)), 1.00
                elif width_factor < height_factor:
                    return float(height_factor.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)), 1.00
                else:
                    return 1.00, 1.00
            case SpriteSetting.ROTATION:
                return 0, 360

    def grab_final_sprite(self) -> QPixmap:
        return self.pixmap()

    def update_sprite(self):
        image = self.sprite_image
        image = image.scaledToHeight(self.sprite_image.height()*self.edit_controls[SpriteSetting.ZOOM.value].value)
        image = image.transformed(QTransform().rotate(self.edit_controls[SpriteSetting.ROTATION.value].value))
        image = image.transformed(QTransform().translate(self.edit_controls[SpriteSetting.HORIZONTAL_OFFSET.value].value,
                                                         self.edit_controls[SpriteSetting.VERTICAL_OFFSET.value].value))
        self.sprite.setPixmap(QPixmap(image))
        self.setPixmap(self.grab_scene_portion(self.sprite_scene,self.sprite_size))

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
        super().__init__(sprite,SpriteType.THUMBNAIL,size)


    def apply_mask_to_pixmap(self, pixmap:QPixmap) -> QPixmap:
        #TODO Needs to apply mask with // Probably only for final image.
        # (Wand) magick image.png mask.png -compose CopyOpacity -composite result.png

        result_pixmap = QPixmap(self.sprite.pixmap().size())
        result_pixmap.fill("transparent")  # This prevents ghost images from showing up

        painter = QPainter(result_pixmap)
        #painter.setRenderHint(QPainter.LosslessImageRendering)

        painter.drawPixmap(0, 0, pixmap)

        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)

        painter.drawImage(0, 0, self.sprite_mask)
        painter.end()

        return result_pixmap

    def update_sprite(self):
        image = self.sprite_image
        image = image.scaledToHeight(self.sprite_image.height() * self.edit_controls[SpriteSetting.ZOOM.value].value)
        image = image.transformed(QTransform().rotate(self.edit_controls[SpriteSetting.ROTATION.value].value))
        image = image.transformed(QTransform().translate(self.edit_controls[SpriteSetting.HORIZONTAL_OFFSET.value].value,
                                                         self.edit_controls[SpriteSetting.VERTICAL_OFFSET.value].value))
        self.sprite.setPixmap(QPixmap(image))
        self.setPixmap(self.apply_mask_to_pixmap(self.grab_scene_portion(self.sprite_scene, self.sprite_size)))

    def calculate_range(self,sprite_setting:SpriteSetting) -> None | tuple[int, int] | tuple[float, float]:
        match sprite_setting:
            case SpriteSetting.HORIZONTAL_OFFSET:
                offset = (self.sprite_image.width() * -1) + 100

                if offset > 0:
                    return 0, offset
                else:
                    return offset, 0

            case SpriteSetting.VERTICAL_OFFSET:
                offset = (self.sprite_image.height() * -1) + 61

                if offset > 0:
                    return 0, offset
                else:
                    return offset, 0
            case SpriteSetting.ZOOM:
                width_factor = Decimal(100 / self.sprite_image.width())
                height_factor = Decimal(61 / self.sprite_image.height())

                if width_factor > height_factor:
                    return float(width_factor.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)), 1.00
                elif width_factor < height_factor:
                    return float(height_factor.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)), 1.00
                else:
                    return 1.00, 1.00
            case SpriteSetting.ROTATION:
                return 0,360
