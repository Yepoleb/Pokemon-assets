#!/usr/bin/env python3

"""
Menu size: 72x120 at 168:0
Description size: 240x40 at 0:120
Text size 240x48 at 0:112
"""

import struct
from tilecodecs import LinearCodec
from tilecodecs import gba
from PIL import Image

# Taken from NSE2 bookmarks
OFFSETS = [
    ("Type1", 0x41f1c8, 0x471dec, 5, 4),
    ("Type2", 0x470b0c, 0x471e0c, 5, 4),
    ("Style0", 0x470D6c, 0x47190c, 3, 3),
    ("Style1", 0x470e8c, 0x47192c, 3, 3),
    ("Style2", 0x47132c, 0x4719ac, 3, 3),
    ("Style3", 0x47144c, 0x4719cc, 3, 3),
    ("Style4", 0x47156c, 0x4719ec, 3, 3),
    ("Style5", 0x4716ac, 0x471a0c, 3, 3),
    ("Style6", 0x4717cc, 0x471a2c, 3, 3)]

ROMPATH = "firered.gba"
with open(ROMPATH, "rb") as rom_file:
    rom = rom_file.read()

codec = LinearCodec(4, LinearCodec.REVERSE_ORDER)
tilesize = codec.getTileSize()

for title, img_offs, pal_offs, tiles_w, tiles_h in OFFSETS:
    palette_data = rom[pal_offs:pal_offs + gba.PALETTE_SIZE]
    palette_rgb = gba.decode_palette(palette_data, alpha=True)
    
    data_len = tiles_w * tiles_h * tilesize
    img_data = rom[img_offs:img_offs + data_len]
    img = gba.decode_image(img_data, codec, palette_rgb, tiles_w)
    img.save("export/textures/textbox_" + title + ".png")

