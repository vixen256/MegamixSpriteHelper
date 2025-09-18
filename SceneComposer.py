from pathlib import Path, PurePath

from PySide6.QtCore import Qt
from enum import Enum, auto
from PIL import Image, ImageOps, ImageQt, ImageStat, ImageShow
from PIL.Image import Resampling

class ThumbnailCheck(Enum):
    FULLY_OPAQUE = [15293.325646817684]
    SPRITE_HELPER_EXPORTED = [15409.511583194137]
    SPRITE_HELPER_EXPORTED_OLD = [15403.198932036757]

class State(Enum):
    FALLBACK = auto()
    IMAGE_TOO_SMALL = auto()
    UPDATED = auto()

class SpriteType(Enum):
    JACKET = auto()
    BACKGROUND = auto()
    THUMBNAIL = auto()
    LOGO = auto()

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
                        "Window Title": f"{(self.type).name} image is too small",
                        "Description": f"{(self.type).name} is too small. Image needs to be at least 1280x720.\nThis doesn't include fully transparent area"
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
        print("background")
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
                    "Window Title": f"{(self.type).name} image is too small",
                    "Description": f"{(self.type).name} is too small. Image needs to be at least 500x500.\nThis doesn't include fully transparent area"
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
        print("jacket")
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
        print("logo")
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
                        "Window Title": f"{(self.type).name} image is too small",
                        "Description": f"{(self.type).name} is too small. Image needs to be at least 100x61.\nThis doesn't include fully transparent area"
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
        print("thumbnail")
        with Image.open(self.location).convert('RGBA') as thumbnail, Image.open(self.script_directory / 'Images/Dummy/Thumbnail-Maskv2.png').convert('L') as mask:
            cropped_thumbnail = Image.Image.crop(thumbnail, Image.Image.getbbox(thumbnail))

            if self.flipped_h:
                cropped_thumbnail = cropped_thumbnail.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            if self.flipped_v:
                cropped_thumbnail = cropped_thumbnail.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

            self.thumbnail_image = ImageOps.scale(cropped_thumbnail.rotate(rotation, Resampling.BILINEAR, expand=True), zoom)
            self.thumbnail = Image.new('RGBA', (128, 64))
            self.thumbnail.alpha_composite(self.thumbnail_image, (horizontal_offset + 28, vertical_offset + 1))
            self.thumbnail_test = Image.composite(self.thumbnail,Image.new('RGBA',(128,64)),mask) #This doesn't fill in transparent area with black. Used only to get info what pixels are filled in.
            self.thumbnail.putalpha(mask) #Used for final image, forces exact same transparency as mask.

class SceneBase:
    def __init__(self):
        self.layers = ()
        self.sprites = []

    def draw_scene(self):
        composite = Image.new('RGBA', (1920, 1080))
        for layer in self.layers:
            sprite, position = layer[0], layer[1]
            composite.alpha_composite(sprite, position)
        return composite

class MegamixSongSelect(SceneBase):
    def __init__(self,background,logo,thumbnail,jacket):
        super().__init__()
        self.required_sprites = [BackgroundSprite,LogoSprite,ThumbnailSprite,JacketSprite]
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
        super().__init__()
        self.required_sprites = [BackgroundSprite,LogoSprite,JacketSprite]
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
        super().__init__()
        self.required_sprites = [LogoSprite,JacketSprite]
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
        super().__init__()
        self.required_sprites = [LogoSprite,JacketSprite]
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
        #Create objects storing information about images
        self.Background = BackgroundSprite(SpriteType.BACKGROUND,Path.cwd() / 'Images/Dummy/SONG_BG_DUMMY.png')
        self.Jacket = JacketSprite(SpriteType.JACKET, Path.cwd() / 'Images/Dummy/SONG_JK_DUMMY.png')
        self.Logo = LogoSprite(SpriteType.LOGO, Path.cwd() / 'Images/Dummy/SONG_LOGO_DUMMY.png')
        self.Thumbnail = ThumbnailSprite(SpriteType.THUMBNAIL, Path.cwd() / 'Images/Dummy/SONG_JK_THUMBNAIL_DUMMY.png')

        self.Megamix_Song_Select = MegamixSongSelect(self.Background,self.Logo,self.Thumbnail,self.Jacket)
        self.Megamix_Result = MegamixResult(self.Background,self.Logo,self.Jacket)
        self.FutureTone_Song_Select = FutureToneSongSelect(self.Background,self.Logo,self.Jacket)
        self.FutureTone_Result = FutureToneResult(self.Logo,self.Jacket)

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


