# Megamix Sprite Helper

Simple program that lets you make slight adjustments to the sprites while having preview of them in most important screens they are used in.

# Features
- Displays a 2x2 grid with both MM UI's and FT UI's Song Select and Results Screen
- - Copy said grid to clipboard for easy sharing
- Edit position, rotation and zoom of the sprites. Big images are cut to optimal shape / size
- - Jacket is processed to get rid of jagged edges from showing up in-game
- - Logo is auto-scaled to fit in allowed area allowing you to work on full resolution images
- Auto updates the preview if loaded images are modified
- Export created sprites directly into Farc or PNG.
- Generate sprite database just by choosing your 2d folder
- Generate combined thumbnail farc

# Notes
- Generating sprite database uses [Hiki8man's Auto create mod_spr_db script](https://gamebanana.com/tools/15812)
- Farc export uses [Vixen256's](https://github.com/vixen256) [Farc](https://github.com/vixen256/farc) and [Spr](https://github.com/vixen256/spr) libraries.
- - Known issue: Exported farc needs to be re-saved with MMM to fix crashes in-game.
- Thumbnail sprite image was made by [ふらすこ](https://www.pixiv.net/en/artworks/134599002)

# Preview

![Megamix Sprite Helper preview](/SpriteHelper-Preview.png)
![Thumbnail Creator preview](/ThumbnailCreator-Preview.png)
