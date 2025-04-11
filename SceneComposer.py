from pathlib import Path, PurePath

from PySide6.QtCore import Qt

from PIL import Image, ImageOps, ImageQt
from PIL.Image import Resampling


class SceneComposer:
    def __init__(self):
        self.script_directory = Path.cwd()

        # Set default sprites for scenes
        self.background_location = self.script_directory / 'Images/Dummy/SONG_BG_DUMMY.png'
        self.jacket_location = self.script_directory / 'Images/Dummy/SONG_JK_DUMMY.png'
        self.logo_location = self.script_directory / 'Images/Dummy/SONG_LOGO_DUMMY.png'
        self.thumbnail_location = self.script_directory / 'Images/Dummy/SONG_JK_THUMBNAIL_DUMMY.png'

    def compose_scene(self,ui_screen):
        self.prepare_scene(ui_screen)
        composite = Image.new('RGBA' ,(1920,1080))
        iteration=0
        for layer in self.grab_layers(ui_screen):
            composite.alpha_composite(layer,self.anchor_points[iteration])
            iteration=iteration+1
        return composite

    def prepare_scene(self,ui_screen):
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
                self.top_layer = Image.open((self.script_directory / 'Images/FT UI - Results Screen/Top Layer.png'))

        pass
    def grab_layers(self,ui_screen):
        match ui_screen:
            case "mm_song_selector":
                self.anchor_points = (
                    (0,0),
                    (0,0),
                    self.mm_song_selector_jacket_anchor_point,
                    (0,0),
                    self.mm_song_selector_logo_anchor_point,
                    (0,0),
                    self.mm_song_selector_thumbnail_1_anchor_point,
                    self.mm_song_selector_thumbnail_2_anchor_point,
                    self.mm_song_selector_thumbnail_3_anchor_point,
                    self.mm_song_selector_selected_thumbnail_anchor_point,
                    self.mm_song_selector_thumbnail_4_anchor_point,
                    self.mm_song_selector_thumbnail_5_anchor_point,
                    self.mm_song_selector_thumbnail_6_anchor_point,
                    self.mm_song_selector_thumbnail_7_anchor_point,
                    (0,0)

                )
                return (
                    self.backdrop,
                    self.scaled_background,
                    self.rotated_jacket,
                    self.middle_layer,
                    self.scaled_logo,
                    self.song_selector,
                    self.resized_thumbnail,
                    self.resized_thumbnail,
                    self.resized_thumbnail,
                    self.resized_selected_thumbnail,
                    self.resized_thumbnail,
                    self.resized_thumbnail,
                    self.resized_thumbnail,
                    self.resized_thumbnail,
                    self.top_layer
                )
            case "mm_result":
                self.anchor_points = (
                    (0,0),
                    (0,0),
                    (0,0),
                    self.mm_result_jacket_anchor_point,
                    self.mm_result_logo_anchor_point,
                    (0,0)
                )
                return (
                    self.backdrop,
                    self.scaled_background,
                    self.middle_layer,
                    self.rotated_jacket,
                    self.scaled_logo,
                    self.top_layer
                )
            case "ft_song_selector":
                self.anchor_points = (
                    (0,0),
                    (0,0),
                    (0,0),
                    self.ft_song_selector_jacket_anchor_point,
                    self.ft_song_selector_logo_anchor_point,
                    (0,0)
                )
                return (
                    self.backdrop,
                    self.scaled_background,
                    self.middle_layer,
                    self.rotated_jacket,
                    self.scaled_logo,
                    self.top_layer
                )
            case "ft_result":
                self.anchor_points = (
                    (0,0),
                    (0,0),
                    self.ft_result_jacket_anchor_point,
                    self.ft_result_logo_anchor_point,
                    (0,0)
                )
                return (
                    self.backdrop,
                    self.middle_layer,
                    self.rotated_jacket,
                    self.scaled_logo,
                    self.top_layer
                )



    def jacket_post_processing(self,horizontal_offset,vertical_offset,rotation,zoom):
        print("jacket")
        self.jacket = Image.new('RGBA',(502,502))
        jacket_image = ImageOps.scale(Image.open(self.jacket_location).convert('RGBA').rotate(rotation, Resampling.BILINEAR,expand=True),zoom)
        self.jacket.alpha_composite(jacket_image,(horizontal_offset,vertical_offset))

        #self.main_box.jacket_horizontal_offset_spinbox.setRange((jacket_scaled.width * -1) + 502, 0)
        #self.main_box.jacket_vertical_offset_spinbox.setRange((jacket_scaled.height * -1) + 502, 0)
        #TODO Fix zoom
    def background_post_processing(self,horizontal_offset,vertical_offset,rotation,zoom):
        print("background")
        background_image = ImageOps.scale(Image.open(self.background_location).convert('RGBA').rotate(rotation,Resampling.BILINEAR,expand=True),zoom)
        self.background = Image.new('RGBA', (1280, 720))
        self.background.alpha_composite(background_image, (horizontal_offset, vertical_offset))
        self.scaled_background = ImageOps.scale(self.background,1.5)

        #self.main_box.background_horizontal_offset_spinbox.setRange((background_scaled.width * -1) + 1280, 0)
        #self.main_box.background_vertical_offset_spinbox.setRange((background_scaled.height * -1) + 720, 0)
        #TODO Fix zoom
    def logo_post_processing(self,state,horizontal_offset,vertical_offset,rotation,zoom):
        print("logo")
        if state == Qt.CheckState.Checked:
            logo_image = ImageOps.scale(Image.open(self.logo_location).convert('RGBA').rotate(rotation,Resampling.BILINEAR,expand=True),zoom)
            self.logo = Image.new('RGBA', (870, 330))
            self.logo.alpha_composite(logo_image, (horizontal_offset, vertical_offset))

            #self.main_box.logo_horizontal_offset_spinbox.setRange((logo_scaled.width * -1) + 435,logo_scaled.width - 435)
            #self.main_box.logo_vertical_offset_spinbox.setRange((logo_scaled.height * -1) + 150,logo_scaled.height - 150)
        else:
            self.logo = Image.new('RGBA', (870, 330))

        #TODO Fix zoom
    def thumbnail_post_processing(self,horizontal_offset,vertical_offset,rotation,zoom):
        print("thumbnail")
        thumbnail_image = ImageOps.scale(Image.open(self.thumbnail_location).convert('RGBA').rotate(rotation,Resampling.BILINEAR,expand=True),zoom)
        self.thumbnail = Image.new('RGBA',(128,64))
        self.thumbnail.alpha_composite(thumbnail_image,(horizontal_offset,vertical_offset))
        self.thumbnail = Image.composite(self.thumbnail,Image.new('RGBA',(128,64)),Image.open(self.script_directory / 'Images/Dummy/Thumbnail-Mask.png').convert('L'))

        #self.main_box.thumbnail_horizontal_offset_spinbox.setRange((thumbnail_scaled.width * -1) +128,27)
        #self.main_box.thumbnail_vertical_offset_spinbox.setRange((thumbnail_scaled.height * -1) + 64,0)
        #TODO Fix zoom