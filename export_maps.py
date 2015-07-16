#!/usr/bin/env python3

import tmx
from bluespider import mapped
from bluespider.mapped import bpre, axve, bpee
from bluespider.mapped import get_banks, get_map_headers, hexbytes, print32bytes
from bluespider.mapped import parse_map_header, parse_map_data, parse_tileset_header
from bluespider.mapped import read_rom_addr_at, get_rom_code, get_rom_data
from PIL import Image, ImageQt

ROMPATH = "firered.gba"

with open(ROMPATH, "rb") as rom_file:
    rom_contents = rom_file.read()

rom_code = get_rom_code(rom_contents)
rom_offsets, game_id = get_rom_data(rom_code)
banks = get_banks(rom_contents, rom_offsets)

map_labels = mapped.get_map_labels(rom_contents,
        rom_offsets, game_id)

with open("offsets.py", "r") as offsetfile:
    offsets = eval(offsetfile.read())

for bank_n in range(len(banks)):
    print("Exporting bank", bank_n)
    map_headers = get_map_headers(rom_contents, bank_n, banks)
    
    for map_n, map_header_address in enumerate(map_headers):
        # Last map, I haven't found a better way to handle this
        if bank_n >= 42 and map_n > 0:
            break

        map_header = parse_map_header(rom_contents, map_header_address)
        map_data_header = mapped.parse_map_data(
                rom_contents, map_header['map_data_ptr'], game_id)
        
        # Parse tile data
        tilemap_ptr = mapped.get_rom_addr(map_data_header['tilemap_ptr'])
        map_size = map_data_header['w'] * map_data_header['h'] * 2
        map_mem = rom_contents[tilemap_ptr:tilemap_ptr+map_size]
        map_data = mapped.parse_map_mem(map_mem, map_data_header['h'],
                map_data_header['w'])
        
        # Parse tileset offsets and label
        global_t = map_data_header['global_tileset_ptr']
        local_t = map_data_header['local_tileset_ptr']
        label_index = map_header['label_index'] - 88
        label = map_labels[label_index]
        
        # Parse events
        events_header = mapped.parse_events_header(rom_contents,
                map_header['event_data_ptr'])
        events = mapped.parse_events(rom_contents, events_header)
        
        # Parse connections
        if map_header['connections_ptr'] == 0:
            connections = []
        else:
            connections_header = mapped.parse_connections_header(rom_contents,
                    map_header['connections_ptr'])
            connections = mapped.parse_connection_data(rom_contents,
                    connections_header)
        
        # Add the tileset offsets to the tile values
        fixed_map = []
        for row in map_data:
            fixed_row = []
            for tile, mov in row:
                if tile > 640: # Local tileset
                    fixed_tile = tile - 640 + offsets[local_t]
                else:
                    fixed_tile = tile + offsets[global_t]
                fixed_row.append((fixed_tile, mov))
            fixed_map.append(fixed_row)
        
        tmx.export_map("export/maps/", bank_n, map_n, label, 
                fixed_map, map_header, events, connections)
