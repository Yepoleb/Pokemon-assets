#!/usr/bin/env python3

from PIL import Image
from tilecodecs import LinearCodec
from tilecodecs import gba
from tilecodecs import Pixmap
from math import ceil

OFFSETS = {
    "font_en_tiny": (0x1eaf00, 0x1eef00),
    "font_jp_tiny": (0x1ef100, 0x1f3100),
    "font_en_other": (0x1f3100, 0x1fb100),
    "font_jp_other": (0x1fb300, 0x1ff300),
    "font_en_black": (0x1ff300, 0x207300),
    "font_jp_black": (0x207500, 0x20f500),
    "font_en_blue": (0x20f618, 0x217618),
    "font_jp_blue": (0x217818, 0x21f818),
    "font_en_red": (0x21f930, 0x227930),
    "font_jp_red": (0x227b30, 0x22fb30),
    "font_jp_tiny2": (0x22fc48, 0x231c48)}

WIDTHS = [
    ("font_en", 0x207300, 0x207500),
    ("font_en_tiny", 0x1eef00, 0x1ef100),
    ("font_jp_black", 0x20f500, 0x20f618),
    ("font_jp_red", 0x22fb30, 0x22fc48),
    ("font_jp_blue", 0x21f818, 0x21f930)]

ROW_LETTERS = 16
IMGSIZE = (256, 512)
EXPDIR = "export/font/"
PIXELCHARS = [" ", "$", ".", "_"]
ROMPATH = "firered.gba"

with open(ROMPATH, "rb") as romfile:
    rom = romfile.read()
codec = LinearCodec(2, LinearCodec.REVERSE_ORDER)


def decode_en(tiles, name):
    img_tiles = list(Pixmap((8,8), tile) for tile in tiles)

    # Each letter has 4 tiles
    letters_n = len(img_tiles) // 4
    img = Pixmap(IMGSIZE)

    for letter_i in range(0, letters_n):
        letter = Pixmap((16,16))
        letter.paste(img_tiles[letter_i*4+1], (0,0))
        letter.paste(img_tiles[letter_i*4+0], (8,0))
        letter.paste(img_tiles[letter_i*4+3], (0,8))
        letter.paste(img_tiles[letter_i*4+2], (8,8))
        
        x = (letter_i % ROW_LETTERS) * 16
        y = (letter_i // ROW_LETTERS) * 16
        img.paste(letter.flip_lr(), (x,y))

    img.save(name, PIXELCHARS)

def decode_jp(tiles, name):
    img_tiles = list(Pixmap((8,8), tile) for tile in tiles)
    
    letters_n = (len(img_tiles)-2) // 4
    img = Pixmap(IMGSIZE)
    
    tilepairs = []
    for i in range(0, len(img_tiles)//2):
        first = (i // 16) * 32 + (i % 16)
        second = first + 16
        tilepair = (img_tiles[first], img_tiles[second])
        tilepairs.append(tilepair)
    
    # The first pair is missing in the original image
    tilepairs = [tilepairs[0]] + tilepairs
    
    for letter_i in range(0, len(tilepairs)//2):
        letter = Pixmap((16,16))
        letter.paste(tilepairs[letter_i*2][0], (0,0))
        letter.paste(tilepairs[letter_i*2][1], (0,8))
        letter.paste(tilepairs[letter_i*2+1][0], (8,0))
        letter.paste(tilepairs[letter_i*2+1][1], (8,8))
        
        x = (letter_i % ROW_LETTERS) * 16
        y = (letter_i // ROW_LETTERS) * 16
        img.paste(letter.flip_lr(), (x,y))

    img.save(name, PIXELCHARS)

def decode_en_tiny(tiles, name):
    img_tiles = list(Pixmap((8,8), tile) for tile in tiles)
    
    letters_n = len(img_tiles) // 2
    img = Pixmap(IMGSIZE)

    # Each letter has 2 tiles
    for letter_i in range(0, letters_n):
        letter = Pixmap((8,16))
        letter.paste(img_tiles[letter_i*2+0], (0,0))
        letter.paste(img_tiles[letter_i*2+1], (0,8))
        
        x = (letter_i % ROW_LETTERS) * 16
        y = (letter_i // ROW_LETTERS) * 16
        img.paste(letter.flip_lr(), (x,y))

    img.save(name, PIXELCHARS)

def decode_jp_tiny(tiles, name):
    img_tiles = list(Pixmap((8,8), tile) for tile in tiles)
    
    letters_n = len(img_tiles) // 2
    img = Pixmap(IMGSIZE)
    
    tilepairs = []
    for i in range(0, len(img_tiles)//2):
        first = (i // 16) * 32 + (i % 16)
        second = first + 16
        tilepair = (img_tiles[first], img_tiles[second])
        tilepairs.append(tilepair)
    
    for letter_i in range(0, len(tilepairs)):
        letter = Pixmap((8,16))
        letter.paste(tilepairs[letter_i][0], (0,0))
        letter.paste(tilepairs[letter_i][1], (0,8))
        
        x = (letter_i % ROW_LETTERS) * 16
        y = (letter_i // ROW_LETTERS) * 16
        img.paste(letter.flip_lr(), (x,y))

    img.save(name, PIXELCHARS)

print("Reading font data")
raw_tiles = {}
for fontname in OFFSETS:
    data = rom[OFFSETS[fontname][0] : OFFSETS[fontname][1]]
    raw_tiles[fontname] = list(gba.iter_decode_tiles(codec, data))

print("Exporting normal fonts")
decode_en(raw_tiles["font_en_black"], EXPDIR + "font_en_black.txt")
decode_jp(raw_tiles["font_jp_black"], EXPDIR + "font_jp_black.txt")
decode_en(raw_tiles["font_en_red"], EXPDIR + "font_en_red.txt")
decode_jp(raw_tiles["font_jp_red"], EXPDIR + "font_jp_red.txt")
decode_en(raw_tiles["font_en_blue"], EXPDIR + "font_en_blue.txt")
decode_jp(raw_tiles["font_jp_blue"], EXPDIR + "font_jp_blue.txt")
decode_en(raw_tiles["font_en_other"], EXPDIR + "font_en_other.txt")
decode_jp_tiny(raw_tiles["font_jp_other"], EXPDIR + "font_jp_other.txt")

print("Exporting tiny fonts")
decode_en_tiny(raw_tiles["font_en_tiny"], EXPDIR + "font_en_tiny.txt")
decode_jp_tiny(raw_tiles["font_jp_tiny"], EXPDIR + "font_jp_tiny.txt")
decode_jp_tiny(raw_tiles["font_jp_tiny2"], EXPDIR + "font_jp_tiny2.txt")

print("Exporting character widths")
for font, start, end in WIDTHS:
    data = rom[start:end]
    out = open(EXPDIR + font + "_width.txt", "w")
    for byte in data:
        out.write(str(byte) + "\n")

