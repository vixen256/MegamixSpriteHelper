from pathlib import Path, PurePath

from PySide6.QtCore import Qt

from PIL import Image, ImageOps, ImageQt
from PIL.Image import Resampling


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


class SceneComposer:
    def __init__(self):
        self.script_directory = Path.cwd()

        # Set defaults for swappable sprites
        self.background_location = self.script_directory / 'Images/Dummy/SONG_BG_DUMMY.png'
        self.jacket_location = self.script_directory / 'Images/Dummy/SONG_JK_DUMMY.png'
        self.logo_location = self.script_directory / 'Images/Dummy/SONG_LOGO_DUMMY.png'
        self.thumbnail_location = self.script_directory / 'Images/Dummy/SONG_JK_THUMBNAIL_DUMMY.png'

    def compose_scene(self,ui_screen,new_classics_state):
            self.prepare_scene(ui_screen,new_classics_state)
            composite = Image.new('RGBA' ,(1920,1080))
            for layer in self.grab_layers(ui_screen):
                sprite, position = layer[0], layer[1]
                composite.alpha_composite(sprite, position)
            return composite

    def prepare_scene(self,ui_screen,new_classics_state):
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
                self.backdrop = Image.open(self.script_directory / 'Images/MM UI - Song Select/Backdrop.png').convert('RGBA')
                self.song_selector = Image.open(self.script_directory / 'Images/MM UI - Song Select/Song Selector.png').convert('RGBA')
                self.middle_layer = Image.open(self.script_directory / 'Images/MM UI - Song Select/Middle Layer.png').convert('RGBA')
                if new_classics_state:
                    self.top_layer = Image.open(self.script_directory / 'Images/MM UI - Song Select/Top Layer - New Classics.png').convert('RGBA')
                else:
                    self.top_layer = Image.open(self.script_directory / 'Images/MM UI - Song Select/Top Layer.png').convert('RGBA')
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
                self.backdrop = ImageOps.scale(Image.open((self.script_directory / 'Images/Dummy/SONG_BG_DUMMY.png')), 1.5)
                self.middle_layer = Image.open((self.script_directory / 'Images/MM UI - Results Screen/Middle Layer.png'))
                if new_classics_state:
                    self.top_layer = Image.open((self.script_directory / 'Images/MM UI - Results Screen/Top Layer - New Classics.png'))
                else:
                    self.top_layer = Image.open((self.script_directory / 'Images/MM UI - Results Screen/Top Layer.png'))

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
                self.backdrop = Image.open((self.script_directory / 'Images/FT UI - Song Select/Base.png'))
                self.middle_layer = Image.open((self.script_directory / 'Images/FT UI - Song Select/Middle Layer.png'))
                if new_classics_state:
                    self.top_layer = Image.open((self.script_directory / 'Images/FT UI - Song Select/Top Layer - New Classics.png'))
                else:
                    self.top_layer = Image.open((self.script_directory / 'Images/FT UI - Song Select/Top Layer.png'))

            case "ft_result":
                # Anchor points and tweaks
                self.ft_result_jacket_anchor_point = (164, 303)
                ft_result_jacket_angle = 5
                self.rotated_jacket = self.jacket.rotate(ft_result_jacket_angle, Resampling.BILINEAR, expand=True)

                self.ft_result_logo_anchor_point = (134, 663)
                ft_result_logo_scale = (0.75)
                self.scaled_logo = ImageOps.scale(self.logo, ft_result_logo_scale)

                self.backdrop = Image.open((self.script_directory / 'Images/FT UI - Results Screen/Base.png'))
                self.middle_layer = Image.open((self.script_directory / 'Images/FT UI - Results Screen/Middle Layer.png'))
                if new_classics_state:
                    self.top_layer = Image.open((self.script_directory / 'Images/FT UI - Results Screen/Top Layer - New Classics.png'))
                else:
                    self.top_layer = Image.open((self.script_directory / 'Images/FT UI - Results Screen/Top Layer.png'))

    def grab_layers(self,ui_screen):
        match ui_screen:
            case "mm_song_selector":
                return (
                    (self.backdrop,(0,0)),
                    (self.scaled_background,(0,0)),
                    (self.rotated_jacket,self.mm_song_selector_jacket_anchor_point),
                    (self.middle_layer,(0,0)),
                    (self.scaled_logo,self.mm_song_selector_logo_anchor_point),
                    (self.song_selector,(0,0)),
                    (self.resized_thumbnail,self.mm_song_selector_thumbnail_1_anchor_point),
                    (self.resized_thumbnail,self.mm_song_selector_thumbnail_2_anchor_point),
                    (self.resized_thumbnail,self.mm_song_selector_thumbnail_3_anchor_point),
                    (self.resized_selected_thumbnail,self.mm_song_selector_selected_thumbnail_anchor_point),
                    (self.resized_thumbnail,self.mm_song_selector_thumbnail_4_anchor_point),
                    (self.resized_thumbnail,self.mm_song_selector_thumbnail_5_anchor_point),
                    (self.resized_thumbnail,self.mm_song_selector_thumbnail_6_anchor_point),
                    (self.resized_thumbnail,self.mm_song_selector_thumbnail_7_anchor_point),
                    (self.top_layer,(0,0))
                )
            case "mm_result":
                return (
                    (self.backdrop,(0,0)),
                    (self.scaled_background,(0,0)),
                    (self.middle_layer,(0,0)),
                    (self.rotated_jacket,self.mm_result_jacket_anchor_point),
                    (self.scaled_logo,self.mm_result_logo_anchor_point),
                    (self.top_layer,(0,0))
                )
            case "ft_song_selector":
                return (
                    (self.backdrop,(0,0)),
                    (self.scaled_background,(0,0)),
                    (self.middle_layer,(0,0)),
                    (self.rotated_jacket,self.ft_song_selector_jacket_anchor_point),
                    (self.scaled_logo,self.ft_song_selector_logo_anchor_point),
                    (self.top_layer,(0,0))
                )
            case "ft_result":
                return (
                    (self.backdrop,(0,0)),
                    (self.middle_layer,(0,0)),
                    (self.rotated_jacket,self.ft_result_jacket_anchor_point),
                    (self.scaled_logo,self.ft_result_logo_anchor_point),
                    (self.top_layer,(0,0))
                )



    def jacket_post_processing(self,horizontal_offset,vertical_offset,rotation,zoom):
        print("jacket")
        with Image.open(self.jacket_location).convert('RGBA') as jacket:
            cropped_jacket = Image.Image.crop(jacket,Image.Image.getbbox(jacket))
            self.jacket = Image.new('RGBA',(500,500))
            self.jacket_image = ImageOps.scale(cropped_jacket.rotate(rotation, Resampling.BILINEAR,expand=True),zoom)
            self.jacket.alpha_composite(self.jacket_image,(horizontal_offset,vertical_offset))
            self.jacket = texture_filtering_fix(self.jacket, 102)
        #TODO Fix zoom
    def background_post_processing(self,horizontal_offset,vertical_offset,rotation,zoom):
        print("background")
        with Image.open(self.background_location).convert('RGBA') as background:
            cropped_background = Image.Image.crop(background,Image.Image.getbbox(background))
            self.background_image = ImageOps.scale(cropped_background.rotate(rotation,Resampling.BILINEAR,expand=True),zoom)
            self.background = Image.new('RGBA', (1280, 720))
            self.background.alpha_composite(self.background_image, (horizontal_offset, vertical_offset))
            self.scaled_background = ImageOps.scale(self.background,1.5)
        #TODO Fix zoom
    def logo_post_processing(self,state,horizontal_offset,vertical_offset,rotation,zoom):
        print("logo")
        if state == Qt.CheckState.Checked:
            with Image.open(self.logo_location).convert('RGBA') as logo:
                self.logo_image = ImageOps.scale(logo.rotate(rotation,Resampling.BILINEAR,expand=True),zoom)
                self.logo = Image.new('RGBA', (870, 330))
                self.logo.alpha_composite(self.logo_image, (horizontal_offset, vertical_offset))
        else:
            self.logo = Image.new('RGBA', (870, 330))
        #TODO Fix zoom
    def thumbnail_post_processing(self,horizontal_offset,vertical_offset,rotation,zoom):
        print("thumbnail")
        with Image.open(self.thumbnail_location).convert('RGBA') as thumbnail ,Image.open(self.script_directory / 'Images/Dummy/Thumbnail-Mask.png').convert('L') as mask:
            self.thumbnail_image = ImageOps.scale(thumbnail.rotate(rotation,Resampling.BILINEAR,expand=True),zoom)
            self.thumbnail = Image.new('RGBA',(128,64))
            self.thumbnail.alpha_composite(self.thumbnail_image,(horizontal_offset,vertical_offset))
            self.thumbnail = Image.composite(self.thumbnail,Image.new('RGBA',(128,64)),mask)
        #TODO Fix zoom