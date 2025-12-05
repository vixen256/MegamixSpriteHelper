from enum import Enum, auto

import KKdLib

class Compression(Enum):
    ATI2 = "YCbCr"
    DXT5 = "DXT5"
    BC7 = "BC7 (Slow)"
    RGBA = "Uncompressed"

    def __str__(self):
        return f"{self.value}"

class FarcCreator:
    def create_jk_bg_logo_farc(self,song_id,jk_bg_texture,logo_texture,output_location,compression:Compression):

        txp = KKdLib.txp_set()
        txp.add_texture_pillow("SH Texture #1",jk_bg_texture,compression.name)

        background = KKdLib.sprite_info()
        background.name = str("SONG_BG" + song_id)
        background.texid = txp.get_texture_id("SH Texture #1")
        background.resolution_mode = "FHD"
        background.x = 2
        background.y = 2
        background.width = 1280
        background.height = 720

        jacket = KKdLib.sprite_info()
        jacket.name = str("SONG_JK" + song_id)
        jacket.texid = txp.get_texture_id("SH Texture #1")
        jacket.resolution_mode = "FHD"
        jacket.x = 1286
        jacket.y = 2
        jacket.width = 502
        jacket.height = 502

        spr = KKdLib.spr_set()


        if logo_texture is not None:
            txp.add_texture_pillow("SH Texture #2",logo_texture,compression.name)

            logo = KKdLib.sprite_info()
            logo.name = str("SONG_LOGO" + song_id)
            logo.texid = txp.get_texture_id("SH Texture #2")
            logo.resolution_mode = "FHD"
            logo.x = 2
            logo.y = 2
            logo.width = 870
            logo.height = 330



        spr.txp = txp
        spr.add_sprite(background)
        spr.add_sprite(jacket)
        if logo_texture is not None:
            spr.add_sprite(logo)

        farc = KKdLib.farc()
        farc.add_file(KKdLib.farc_file(name="spr_sel_pv"+song_id+".bin", data=spr.pack()))
        farc.write(output_location+'/spr_sel_pv'+song_id+'.farc')

    def create_thumbnail_farc(self,thumb_data,thumbnail_texture,output_location,mod_name,compression:Compression):
        txp = KKdLib.txp_set()
        txp.add_texture_pillow("SH Texture #1", thumbnail_texture,compression.name)

        spr = KKdLib.spr_set()
        spr.txp = txp

        for thumb in thumb_data:
            #[id,(x,y)]
            thumbnail = KKdLib.sprite_info()
            thumbnail.name = thumb[0]
            thumbnail.texid = txp.get_texture_id("SH Texture #1")
            thumbnail.resolution_mode = "FHD"
            thumbnail.x = thumb[1][0]
            thumbnail.y = thumb[1][1]
            thumbnail.width = 128
            thumbnail.height = 64

            spr.add_sprite(thumbnail)

        farc = KKdLib.farc()
        farc.add_file(KKdLib.farc_file(name="spr_sel_pvtmb_"+mod_name+".bin", data=spr.pack()))
        farc.write(output_location + '/spr_sel_pvtmb_' + mod_name + '.farc')