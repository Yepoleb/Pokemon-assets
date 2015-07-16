import tmxlib

# layer_name, event_type, color
EVENTTYPES = (
        ("People",    "person",   (219,  0,  0)),
        ("Warps",     "warp",     (  0,109,109)),
        ("Triggers",  "trigger",  (  0,150,  0)),
        ("Signposts", "signpost", (219,219,  0)))

CONNECTIONS_COLOR = (255/255, 128/255, 0/255)

def flat(lst):
    """Turns a 2D list into a 1D one"""
    flatened = []
    for element in lst:
        flatened += element
    return flatened

def export_map(path, bank_n, map_n, label, tiledata, header, eventdata, 
        connectiondata):
    height = len(tiledata)
    width = len(tiledata[0])
    hpixel = height * 16
    wpixel = width * 16

    tmxmap = tmxlib.map.Map((width, height), (16, 16))

    # Add the tileset prototypes
    lowimg = tmxlib.image.open("../textures/blocks0.png", size=(2048, 1264))
    highimg = tmxlib.image.open("../textures/blocks1.png", size=(2048, 1264))
    movementimg = tmxlib.image.open("../textures/movement.png", size=(128, 128))
    lowts = tmxlib.tileset.ImageTileset("Low", (16, 16), lowimg, source="../textures/low.tsx")
    hights = tmxlib.tileset.ImageTileset("High", (16, 16), highimg, source="../textures/high.tsx")
    movementts = tmxlib.tileset.ImageTileset("Movement", (16, 16), movementimg)
    tmxmap.tilesets.append(lowts)
    tmxmap.tilesets.append(hights)
    tmxmap.tilesets.append(movementts)

    lowdata = list(t[0]+lowts.first_gid(tmxmap) for t in flat(tiledata))
    # High has the same data as low with a static offset
    highdata = list(t[0]+hights.first_gid(tmxmap) for t in flat(tiledata))
    movementdata = list(t[1]+movementts.first_gid(tmxmap) for t in flat(tiledata))

    low = tmxlib.layer.TileLayer(tmxmap, "Low", visible=True, data=lowdata)
    high = tmxlib.layer.TileLayer(tmxmap, "High", visible=True, data=highdata)
    movement = tmxlib.layer.TileLayer(tmxmap, "Movement", visible=False, opacity=0.5, data=movementdata)
    low.encoding = "csv"
    high.encoding = "csv"
    movement.encoding = "csv"
    tmxmap.layers.append(low)
    tmxmap.layers.append(high)
    tmxmap.layers.append(movement)

    connections = tmxlib.layer.ObjectLayer(tmxmap, "Connections", visible=True, color=CONNECTIONS_COLOR)
    for connection in connectiondata:
        direction = connection["direction"]
        pos = (0, 0)
        size = (0, 0)
        if direction == 1:
            pos = (0, hpixel)
            size = (wpixel, 8)
        elif direction == 2:
            pos = (0, 8)
            size = (wpixel, 8)
        elif direction == 3:
            pos = (0, hpixel)
            size = (8, hpixel)
        elif direction == 4:
            pos = (wpixel-8, hpixel)
            size = (8, hpixel)
        connobj = tmxlib.mapobject.RectangleObject(connections, pos, pixel_size=size, 
                name=str(direction), type="connection")
        for key in connection:
            if key == "null":
                continue
            connobj.properties[key] = str(connection[key])
        connections.append(connobj)
    tmxmap.layers.append(connections)

    for i, (layer_name, event_type, color) in enumerate(EVENTTYPES):
        floatcolor = tuple(x/255 for x in color)
        layer = tmxlib.layer.ObjectLayer(tmxmap, layer_name, True, color=floatcolor)
        for num, event in enumerate(eventdata[i]):
            x = (event["x"]) * 16
            y = (event["y"]+1) * 16
            mapobj = tmxlib.mapobject.RectangleObject(layer, (x, y), (1,1), 
                    name=str(num), type=event_type)
            for key in event:
                mapobj.properties[key] = str(event[key])
            layer.append(mapobj)
        tmxmap.layers.append(layer)

    for key in header:
        tmxmap.properties[key] = str(header[key])
    tmxmap.properties["label"] = label

    tmxmap.save(path + "{}.{} {}.tmx".format(bank_n, map_n, label))

def export_tileset(name, path, img, behavior_data):
    timg = tmxlib.image.open(img, size=(2048, 1264))
    ts = tmxlib.tileset.ImageTileset(name, (16,16), timg)
    for i in range(len(behavior_data)//4):
        bbytes = behavior_data[i*4:(i+1)*4]
        behavior = hex(int.from_bytes(bbytes[0:2], "little"))
        background = hex(int.from_bytes(bbytes[2:4], "little"))
        ts[i].properties = {"background": background, "behavior": behavior}
    ts.save(path)

