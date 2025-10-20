import spr
import farc

class FarcCreator:
    def create_jk_bg_logo_farc(self,song_id,jk_bg_texture,logo_texture,output_location,is_logo_checked):
        sprite_set = spr.PySprSet()
        sprite_set.set_texture(('MERGE_D5COMP_0'),spr.PyImage(jk_bg_texture))

        background = spr.PySprite()
        background.texture = 'MERGE_D5COMP_0'
        background.screen_mode = spr.ScreenMode.HDTV1080
        background.x = 2
        background.y = 2
        background.width = 1280
        background.height = 720

        jacket = spr.PySprite()
        jacket.texture = 'MERGE_D5COMP_0'
        jacket.screen_mode = spr.ScreenMode.HDTV1080
        jacket.x = 1286
        jacket.y = 2
        jacket.width = 502
        jacket.height = 502

        sprite_set.set_sprite(str("SONG_BG" + song_id), background)
        sprite_set.set_sprite(str("SONG_JK" + song_id), jacket)

        if is_logo_checked:
            sprite_set.set_texture(('MERGE_D5COMP_1'),spr.PyImage(logo_texture))

            logo = spr.PySprite()
            logo.texture = 'MERGE_D5COMP_1'
            logo.screen_mode = spr.ScreenMode.HDTV1080
            logo.x = 2
            logo.y = 2
            logo.width = 870
            logo.height = 330

            sprite_set.set_sprite(str("SONG_LOGO" + song_id), logo)


        files = {"spr_sel_pv"+song_id+".bin": sprite_set.save_to_raw()}
        farc.save(files,output_location+'/spr_sel_pv'+song_id+'.farc', True)

    def create_thumbnail_farc(self,thumb_data,thumbnail_texture,output_location,mod_name):
        sprite_set = spr.PySprSet()
        sprite_set.set_texture(('MERGE_D5COMP_0'), spr.PyImage(thumbnail_texture))

        for thumb in thumb_data:
            #[id,(x,y)]
            thumbnail = spr.PySprite()
            thumbnail.texture = 'MERGE_D5COMP_0'
            thumbnail.screen_mode = spr.ScreenMode.HDTV1080
            thumbnail.x = thumb[1][0]
            thumbnail.y = thumb[1][1]
            thumbnail.width = 128
            thumbnail.height = 64

            sprite_set.set_sprite(str(thumb[0]),thumbnail)

        files = {"spr_sel_pvtmb_"+mod_name+".bin": sprite_set.save_to_raw()}
        farc.save(files, str(output_location) + '/spr_sel_pvtmb_' + mod_name + '.farc', True)
        print(str(output_location) + '/spr_sel_pvtmb_' + mod_name + '.farc')

        #Sorting doesn't work properly. Instead of sorting by number it treats them as strings.