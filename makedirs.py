#!/usr/bin/env python3

import os

DIRS = ["export/maps", "export/sprites", "export/font", "export/textures"]

for path in DIRS:
    os.makedirs(path, exist_ok=True)
