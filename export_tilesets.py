#!/usr/bin/env python3

import tmx
from bluespider import mapped
from bluespider.mapped import bpre, axve, bpee
from bluespider.mapped import get_banks, get_map_headers, hexbytes, print32bytes
from bluespider.mapped import parse_map_header, parse_map_data, parse_tileset_header
from bluespider.mapped import read_rom_addr_at, get_rom_code, get_rom_data
from bluespider.mapped import GRAYSCALE
from PIL import Image, ImageQt

ROMPATH = "firered.gba"
TILES_PER_ROW = 128 # Set to 8 for a human readable tileset

def get_behavior_data(rom_contents, tileset_header, game='RS'):
    behavior_data_ptr = mapped.get_rom_addr(tileset_header['behavior_data_ptr'])
    t_type = tileset_header['tileset_type']
    if t_type == 0:
        if game == 'RS' or game == 'EM':
            num_of_blocks = 512
        else:
            num_of_blocks = 640
    else:
        block_data_ptr = mapped.get_rom_addr(tileset_header['block_data_ptr'])
        num_of_blocks = (behavior_data_ptr - block_data_ptr) // 16
    length = num_of_blocks*16
    mem = rom_contents[behavior_data_ptr:behavior_data_ptr+num_of_blocks*4]
    return mem

def build_block_imgs(blocks_mem, imgs, palettes, behavior):
    ''' Build images from the block information and tilesets.
     Every block is 16 bytes, and holds down and up parts for a tile,
     composed of 4 subtiles
     every subtile is 2 bytes
     1st byte and 2nd bytes last (two?) bit(s) is the index in the tile img
     2nd byte's first 4 bits is the color palette index
     2nd byte's final 4 bits is the flip information... and something else,
     I guess
         0b0100 = x flip
     '''
    # TODO: Optimize. A lot.
    block_imgs = []
    tiles_per_line = 16
    base_block_img = Image.new("RGBA", (16, 16))
    mask = Image.new("L", (8, 8))
    positions = {
            0: (0,0),
            1: (8,0),
            2: (0,8),
            3: (8,8)
          }
    for block in range(len(blocks_mem)//16):
        block_mem = blocks_mem[block*16:block*16+16]
        beh_mem = int.from_bytes(behavior[block*4:block*4+4], "big")
        layer_imgs = []
        # Up/down
        for layer in range(2):
            layer_mem = block_mem[layer*8:layer*8+8]
            if (beh_mem & 0x20) and layer == 1:
                block_img = layer_imgs[0]
            else:
                block_img = base_block_img.copy()
            for part in range(4):
                d = part*2
                byte1 = layer_mem[d]
                byte2 = layer_mem[d+1]
                tile_num = byte1 | ((byte2 & 0b11) << 8)
                palette_num = byte2 >> 4
                if palette_num >= 13: # XXX
                    palette_num = 0
                palette = GRAYSCALE or palettes[palette_num]
                img = imgs[palette_num]
                flips = (byte2 & 0xC) >> 2
                x = (tile_num % tiles_per_line) * 8
                y = (tile_num // tiles_per_line) * 8
                pos = (x, y, x+8, y+8)
                part_img = img.crop(pos)
                if flips & 1:
                    part_img = part_img.transpose(Image.FLIP_LEFT_RIGHT)
                if flips & 2:
                    part_img = part_img.transpose(Image.FLIP_TOP_BOTTOM)
                x, y = positions[part]
                # Transparency
                #mask = Image.eval(part_img, lambda a: 255 if a else 0)
                t = palette[0]
                if layer:
                    img_data = tuple(part_img.getdata())
                    #mask_data = tuple(map(lambda p : (0 if p == t else 255),
                    #                  img_data))
                    mask_data = [0 if i == t else 255 for i in img_data]
                    mask.putdata(mask_data)
                    block_img.paste(part_img, (x, y, x+8, y+8), mask)
                else:
                    block_img.paste(part_img, (x, y, x+8, y+8))

            if (beh_mem & 0x20) and layer == 1:
                layer_imgs.append(base_block_img.copy())
            else:
                layer_imgs.append(block_img)
        block_imgs.append(layer_imgs)
    return block_imgs

with open(ROMPATH, "rb") as rom_file:
    rom_contents = rom_file.read()

rom_code = get_rom_code(rom_contents)
rom_offsets, game_id = get_rom_data(rom_code)
banks = get_banks(rom_contents, rom_offsets)

tilesets = set()
offsets = {}

# Loop over all maps and add their tileset offsets
for bank_n in range(len(banks)):
    map_headers = get_map_headers(rom_contents, bank_n, banks)
    
    for map_n, map_header_address in enumerate(map_headers):
        # Last map, I haven't found a better way to handle this
        if bank_n >= 42 and map_n > 0:
            break

        map_header = parse_map_header(rom_contents, map_header_address)
        map_data_header = mapped.parse_map_data(
            rom_contents, map_header['map_data_ptr'], game_id)
        tilesets.add((
            map_data_header['global_tileset_ptr'], 
            map_data_header['local_tileset_ptr']))

global_blocks = {}
local_blocks = {}
global_behavior = {}
local_behavior = {}

for tileset1, tileset2 in list(tilesets):
    t1_header = mapped.parse_tileset_header(rom_contents, tileset1, game_id)
    t2_header = mapped.parse_tileset_header(rom_contents, tileset2, game_id)
    
    pals1_ptr = mapped.get_rom_addr(t1_header["palettes_ptr"])
    pals2_ptr = mapped.get_rom_addr(t2_header["palettes_ptr"])
    pals = mapped.get_pals(rom_contents, game_id, pals1_ptr, pals2_ptr)
    imgs = mapped.load_tilesets(rom_contents, game_id, t1_header, t2_header, pals)
    
    # Check if the tileset has been rendered already
    if tileset1 not in global_blocks:
        print(hex(tileset1))
        behavior_data1 = get_behavior_data(rom_contents, t1_header, game_id)
        global_behavior[tileset1] = behavior_data1
        
        block_data_mem = mapped.get_block_data(rom_contents, t1_header, game_id)
        blocks_imgs = build_block_imgs(
            block_data_mem, imgs, pals, behavior_data1)
        global_blocks[tileset1] = blocks_imgs
    
    if tileset2 not in local_blocks:
        print(hex(tileset2))
        behavior_data2 = get_behavior_data(rom_contents, t2_header, game_id)
        local_behavior[tileset2] = behavior_data2
        
        block_data_mem = mapped.get_block_data(rom_contents, t2_header, game_id)
        blocks_imgs = build_block_imgs(
            block_data_mem, imgs, pals, behavior_data2)
        local_blocks[tileset2] = blocks_imgs


blocks_imgs = []
behavior_bytes = bytes()

# Join all tilesets into a big one
print("Joining tilesets")
for addr, blocks in global_blocks.items():
    offsets[addr] = len(blocks_imgs)
    blocks_imgs += blocks
    behavior_bytes += global_behavior[addr]
for addr, blocks in local_blocks.items():
    offsets[addr] = len(blocks_imgs)
    blocks_imgs += blocks
    behavior_bytes += local_behavior[addr]



blocks_img_w = 16 * TILES_PER_ROW
blocks_img_h = (len(blocks_imgs) // TILES_PER_ROW) * 16
for layer in range(2):
    blocks_img = Image.new("RGBA", (blocks_img_w, blocks_img_h))
    block_i = 0
    for row in range(blocks_img_h // 16):
        for col in range(blocks_img_w // 16):
            pos = (col*16, row*16)
            blocks_img.paste(blocks_imgs[block_i][layer], pos)
            block_i += 1
    blocks_img.save("export/textures/blocks"+str(layer)+".png")

tmx.export_tileset("Low",
        "export/textures/low.tsx", 
        "blocks0.png",
        behavior_bytes)
tmx.export_tileset("High",
        "export/textures/high.tsx", 
        "blocks1.png",
        [])

# Store the offsets to load them in exports_maps
with open("offsets.py", "w") as offsetfile:
    offsetfile.write(str(offsets))
