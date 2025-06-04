# Megamix Sprite Helper

Simple program that lets you make slight adjustments to the sprites while having preview of them in most important screens they are used it.

# Features
- Displays a 2x2 grid with both MM UI and FT UI's Song Select and Results Screen
- Edit position, rotation and zoom of the sprites. Big images are cut to optimal shape / size
- Copy said grid to clipboard for easy sharing
- Auto updates the preview if loaded images are modified
- Export Background/Jacket, logo and single thumbnail texture to png
- On export of Background/Jacket texture applies fix for jagged edges of jacket.
- Generate sprite database just by choosing your 2d folder

# Notes
- Generating sprite database uses [Hiki8man's Auto create mod_spr_db script](https://gamebanana.com/tools/15812)

# For sprites to be properly aligned you need to set those coords/sizes in Farc file.

SONG_BG:

X = 2
Y = 2
Width = 1280
Height = 720


SONG_JK:

X = 1286
Y = 2
Width = 502
Height = 502

SONG_LOGO:

X = 2
Y = 2
Width = 870
Height = 330

# Preview

![Megamix Sprite Helper preview](/SpriteHelper-Preview.png)
