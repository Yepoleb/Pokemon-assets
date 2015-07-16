#!/usr/bin/env python3

from tilecodecs import LinearCodec
from tilecodecs import gba
from bluespider import lz77
import copy

bkgr_addr = 0xE830CC
bkgr_maps_addr = [0xE83444, 0xE832C0]
bkgr_palettes_addr = [0xE835B4, 0xE83604]
bag_male = 0xE8362C
bag_female = 0xE83DBC
bag_palette = 0xE84560
arrow_addr = 0xE84588
arrow_palette_addr = 0xE845C8

ROMPATH = "firered.gba"
GENDERNAMES = ["male", "female"]

with open(ROMPATH, "rb") as romfile:
    rom = romfile.read()

codec = LinearCodec(4, LinearCodec.REVERSE_ORDER)

bag_male_data = lz77.decompress(rom[bag_male:])
bag_female_data = lz77.decompress(rom[bag_female:])
bag_palette_data = lz77.decompress(rom[bag_palette:])

bag_palette_pal = gba.decode_palette(bag_palette_data, alpha=True)
bag_male_img = gba.decode_image(bag_male_data, codec, bag_palette_pal, 8)
bag_male_img.save("export/textures/bag_male.png")
bag_female_img = gba.decode_image(bag_female_data, codec, bag_palette_pal, 8)
bag_female_img.save("export/textures/bag_female.png")

arrow_data = lz77.decompress(rom[arrow_addr:])
arrow_palette_data = lz77.decompress(rom[arrow_palette_addr:])
arrow_palette = gba.decode_palette(arrow_palette_data, alpha=True)
arrow_image = gba.decode_image(arrow_data, codec, arrow_palette, 2)
arrow_image.save("export/textures/arrow.png")

bkgr_data = lz77.decompress(rom[bkgr_addr:])
bkgr_tiles = list(gba.iter_decode_tiles(codec, bkgr_data))

bkgr_palettes = [None, None]
bkgr_palettes_data0 = lz77.decompress(rom[bkgr_palettes_addr[0]:])
bkgr_palettes_data1 = lz77.decompress(rom[bkgr_palettes_addr[1]:])
bkgr_palettes[0] = list(gba.iter_decode_palettes(bkgr_palettes_data0, alpha=True))
bkgr_palettes[1] = copy.copy(bkgr_palettes[0])
bkgr_palettes[1][0] = gba.decode_palette(bkgr_palettes_data1)

for mode in (0,1):
    bkgr_map = lz77.decompress(rom[bkgr_maps_addr[mode]:])
    for gender in (0,1):
        bkgr_map_tiles = gba.decode_tilemap(bkgr_map, bkgr_tiles, bkgr_palettes[gender])
        bkgr_img = gba.combine_tiles(bkgr_map_tiles, 32)
        bkgr_img = bkgr_img.crop((0, 0, 240, 160))
        bkgr_img.save("export/textures/background{}_{}.png".format(mode, GENDERNAMES[gender]))
