#!/usr/bin/env python3

"""
Sources:
Overworld Editor Reloaded (frmOverworldEditor.frm, modGraphicEditing.bas)
"""

import struct
import math
from PIL import Image
from tilecodecs import LinearCodec
from tilecodecs import gba
from collections import namedtuple

OUTPUT_PATH = "export/sprites/"

ORDER_PTR = 0x39FDB0
BANK_PTR = 0x3A3BB0 #lngSpriteBank
PALETTES_PTR = 0x3A5158 #lngSpritePaletteHeaders
SPRITE_COUNT = 153 #bytSpriteMax
PALETTE_COUNT = 18
FRAME_LIMITS = [
    19, 8, 11, 8, 8, 8, 8, 8, 9, 8, 9, 9, 9, 8, 9, 9, 9, 8, 9, 9, 9, 
    8, 8, 9, 8, 8, 8, 9, 9, 9, 9, 9, 9, 8, 9, 9, 9, 9, 9, 9, 9, 9, 
    8, 9, 8, 8, 9, 9, 9, 9, 9, 8, 9, 8, 0, 8, 9, 9, 8, 8, 8, 3, 8, 
    8, 8, 8, 8, 3, 0, 19, 8, 11, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 
    8, 8, 8, 8, 8, 8, 11, 11, 8, 5, 8, 5, 0, 0, 8, 8, 0, 0, 0, 0, 0, 
    0, 0, 0, 0, 0, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 
    8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 
    8, 8, 8, 8, 8, 8]

ROMPATH = "firered.gba"
with open(ROMPATH, "rb") as romfile:
    rom = romfile.read()

codec = LinearCodec(4, LinearCodec.REVERSE_ORDER)


SpriteHeaderFMT = "<HBBBBHHHBBHIIIII"
SpriteHeaderSize = struct.calcsize(SpriteHeaderFMT)
SpriteHeader = namedtuple("SpriteHeader",
        "starter_bytes, palette_modifier, unknown1, unknown2, unknown3, \
        data_size, width, height, unknown4, unknown5, unknown6, pointer1, \
        pointer2, pointer3, header2_pointer, pointer4")

SpriteHeader2FMT = "<IHH"
SpriteHeader2Size = struct.calcsize(SpriteHeader2FMT)
SpriteHeader2 = namedtuple("SpriteHeader2",
        "sprite_pointer, data_size, unknown")

PaletteHeaderFMT = "<IBBBB"
PaletteHeaderSize = struct.calcsize(PaletteHeaderFMT)
PaletteHeader = namedtuple("PaletteHeader",
        "data_pointer, index, unknown1, unknown2, unknown3")



palette_headers = {}
palette_header_data = rom[PALETTES_PTR:PALETTES_PTR+PaletteHeaderSize*PALETTE_COUNT]
for palette_header in struct.iter_unpack(PaletteHeaderFMT, palette_header_data):
    palette_header = PaletteHeader._make(palette_header)
    palette_headers[palette_header.index] = palette_header

palettes = {}
for i in palette_headers.keys():
    palette_offset = palette_headers[i].data_pointer - 0x8000000
    palette_data = rom[palette_offset:palette_offset + gba.PALETTE_SIZE]
    palette = gba.decode_palette(palette_data, alpha=True)
    palettes[i] = palette

sheetorder = []
for i in range(SPRITE_COUNT):
    h1_ptr = struct.unpack_from("I", rom, ORDER_PTR + (4*i))[0] - 0x8000000
    sheetorder.append(h1_ptr)

for i in range(SPRITE_COUNT):
    h1_ptr = BANK_PTR + (SpriteHeaderSize * i)
    spriteh1 = SpriteHeader._make(struct.unpack_from(SpriteHeaderFMT, rom, h1_ptr))
    width = spriteh1.width
    height = spriteh1.height
    frames = FRAME_LIMITS[i] + 1
    
    if frames < 3:
        sheetwidth = frames
    else:
        sheetwidth = 3
    

    sheetheight = int(math.ceil(frames / 3))
    sheetpixel = (sheetwidth * width, sheetheight * height)
    sheet = Image.new("RGBA", sheetpixel)
    
    for frame in range(frames):
        spriteh2 = SpriteHeader2._make(struct.unpack_from(SpriteHeader2FMT, rom, 
                spriteh1.header2_pointer - 0x8000000 + (SpriteHeader2Size * frame)))

        spriteoffset = spriteh2.sprite_pointer - 0x8000000
        data = rom[spriteoffset:spriteoffset+spriteh2.data_size]
        palette = palettes[spriteh1.palette_modifier]
        img = gba.decode_image(data, codec, palette, width // 8)
        
        sheetpos = (frame % 3 * width, frame // 3 * height)
        sheet.paste(img, sheetpos)
    
    try:
        sprite_num = sheetorder.index(h1_ptr)
    except:
        print(h1_ptr, "not found")
        continue
    sheet.save(OUTPUT_PATH + "{} {}x{}.png".format(sprite_num, width, height))

