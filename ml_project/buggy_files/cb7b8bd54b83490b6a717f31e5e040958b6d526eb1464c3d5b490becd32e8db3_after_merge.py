def read_tiled_map(tmx_file: str, scaling: float = 1, tsx_file: str = None) -> TiledMap:
    """
    Given a tmx_file, this will read in a tiled map, and return
    a TiledMap object.

    Given a tsx_file, the map will use it as the tileset.
    If tsx_file is not specified, it will use the tileset specified
    within the tmx_file.

    Important: Tiles must be a "collection" of images.

    Hitboxes can be drawn around tiles in the tileset editor,
    but only polygons are supported.
    (This is a great area for PR's to improve things.)

    :param str tmx_file: String with name of our TMX file
    :param float scaling: Scaling factor. 0.5 will half all widths and heights
    :param str tsx_file: Tileset to use (can be specified in TMX file)

    :returns: Map
    :rtype: TiledMap
    """

    # Create a map object to store this stuff in
    my_map = TiledMap()

    # Read in and parse the file
    tree = etree.parse(tmx_file)

    # Root node should be 'map'
    map_tag = tree.getroot()

    # Pull attributes that should be in the file for the map
    my_map.version = map_tag.attrib["version"]
    my_map.orientation = map_tag.attrib["orientation"]
    my_map.renderorder = map_tag.attrib["renderorder"]
    my_map.width = int(map_tag.attrib["width"])
    my_map.height = int(map_tag.attrib["height"])
    my_map.tilewidth = int(map_tag.attrib["tilewidth"])
    my_map.tileheight = int(map_tag.attrib["tileheight"])

    # Background color is optional, and may or may not be in there
    if "backgroundcolor" in map_tag.attrib:
        # Decode the background color string
        backgroundcolor_string = map_tag.attrib["backgroundcolor"]
        red_hex = "0x" + backgroundcolor_string[1:3]
        green_hex = "0x" + backgroundcolor_string[3:5]
        blue_hex = "0x" + backgroundcolor_string[5:7]
        red = int(red_hex, 16)
        green = int(green_hex, 16)
        blue = int(blue_hex, 16)
        my_map.backgroundcolor = (red, green, blue)

    my_map.nextobjectid = map_tag.attrib["nextobjectid"]

    # Grab all the tilesets
    tileset_tag_list = map_tag.findall('./tileset')

    # --- Tileset Data ---

    # Loop through each tileset
    for tileset_tag in tileset_tag_list:
        firstgid = int(tileset_tag.attrib["firstgid"])
        if tsx_file is not None or "source" in tileset_tag.attrib:
            if tsx_file is not None:
                tileset_tree = etree.parse(tsx_file)
            else:
                source = tileset_tag.attrib["source"]
                try:
                    tileset_tree = etree.parse(source)
                except FileNotFoundError:
                    source = Path(tmx_file).parent / Path(source)
                    tileset_tree = etree.parse(source)
            # Root node should be 'map'
            tileset_root = tileset_tree.getroot()
            tile_tag_list = tileset_root.findall("tile")
        else:
            # Grab each tile
            tile_tag_list = tileset_tag.findall("tile")

        # Loop through each tile
        for tile_tag in tile_tag_list:
            # Make a tile object
            my_tile = Tile()
            image = tile_tag.find("image")
            my_tile.local_id = tile_tag.attrib["id"]
            my_tile.width = int(image.attrib["width"])
            my_tile.height = int(image.attrib["height"])
            my_tile.source = image.attrib["source"]
            key = str(int(my_tile.local_id) + 1)
            my_map.global_tile_set[key] = my_tile
            firstgid += 1

            objectgroup = tile_tag.find("objectgroup")
            if objectgroup:
                my_object = objectgroup.find("object")
                if my_object:
                    offset_x = round(float(my_object.attrib['x']))
                    offset_y = round(float(my_object.attrib['y']))

                    polygon = my_object.find("polygon")
                    if polygon is not None:
                        point_list = _parse_points(polygon.attrib['points'])
                        for point in point_list:
                            point[0] += offset_x
                            point[1] += offset_y
                            point[1] = my_tile.height - point[1]
                            point[0] -= my_tile.width // 2
                            point[1] -= my_tile.height // 2
                            point[0] *= scaling
                            point[1] *= scaling
                            point[0] = int(point[0])
                            point[1] = int(point[1])

                        my_tile.points = point_list

                    polygon = my_object.find("polyline")
                    if polygon is not None:
                        point_list = _parse_points(polygon.attrib['points'])
                        for point in point_list:
                            point[0] += offset_x
                            point[1] += offset_y
                            point[1] = my_tile.height - point[1]
                            point[0] -= my_tile.width // 2
                            point[1] -= my_tile.height // 2
                            point[0] *= scaling
                            point[1] *= scaling
                            point[0] = int(point[0])
                            point[1] = int(point[1])

                        if point_list[0][0] != point_list[-1][0] or point_list[0][1] != point_list[-1][1]:
                            point_list.append([point_list[0][0], point_list[0][1]])

                        my_tile.points = point_list

    # --- Map Data ---

    # Grab each layer
    layer_tag_list = map_tag.findall('./layer')
    for layer_tag in layer_tag_list:
        layer_width = int(layer_tag.attrib['width'])

        # Unzip and unencode each layer
        data = layer_tag.find("data")
        data_text = data.text.strip()
        encoding = data.attrib['encoding']
        if 'compression' in data.attrib:
            compression = data.attrib['compression']
        else:
            compression = None

        if encoding == "csv":
            layer_grid_ints = _process_csv_encoding(data_text)
        elif encoding == "base64":
            layer_grid_ints = _process_base64_encoding(data_text, compression, layer_width)
        else:
            print(f"Error, unexpected encoding: {encoding}.")
            break

        # Great, we have a grid of ints. Save that according to the layer name
        my_map.layers_int_data[layer_tag.attrib["name"]] = layer_grid_ints

        # Now create grid objects for each tile
        layer_grid_objs = []
        for row_index, row in enumerate(layer_grid_ints):
            layer_grid_objs.append([])
            for column_index, column in enumerate(row):
                grid_loc = GridLocation()
                if layer_grid_ints[row_index][column_index] != 0:
                    key = str(layer_grid_ints[row_index][column_index])

                    if key not in my_map.global_tile_set:
                        print(f"Warning, tried to load '{key}' and it is not in the tileset.")
                    else:
                        grid_loc.tile = my_map.global_tile_set[key]

                        if my_map.renderorder == "right-down":
                            adjusted_row_index = my_map.height - row_index - 1
                        else:
                            adjusted_row_index = row_index

                        if my_map.orientation == "orthogonal":
                            grid_loc.center_x = column_index * my_map.tilewidth + my_map.tilewidth // 2
                            grid_loc.center_y = adjusted_row_index * my_map.tileheight + my_map.tilewidth // 2
                        else:
                            grid_loc.center_x,  grid_loc.center_y = isometric_grid_to_screen(column_index,
                                                                                             row_index,
                                                                                             my_map.width,
                                                                                             my_map.height,
                                                                                             my_map.tilewidth,
                                                                                             my_map.tileheight)

                layer_grid_objs[row_index].append(grid_loc)

        my_map.layers[layer_tag.attrib["name"]] = layer_grid_objs

    return my_map