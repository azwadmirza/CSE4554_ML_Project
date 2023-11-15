def generate_sprites(map_object, layer_name, scaling, base_directory=""):
    sprite_list = SpriteList()

    if layer_name not in map_object.layers_int_data:
        print(f"Warning, no layer named '{layer_name}'.")
        return sprite_list

    map_array = map_object.layers_int_data[layer_name]

    # Loop through the layer and add in the wall list
    for row_index, row in enumerate(map_array):
        for column_index, item in enumerate(row):
            if str(item) in map_object.global_tile_set:
                tile_info = map_object.global_tile_set[str(item)]
                tmx_file = base_directory + tile_info.source

                my_sprite = Sprite(tmx_file, scaling)
                my_sprite.right = column_index * (map_object.tilewidth * scaling)
                my_sprite.top = (map_object.height - row_index) * (map_object.tileheight * scaling)

                if tile_info.points is not None:
                    my_sprite.set_points(tile_info.points)
                sprite_list.append(my_sprite)
            elif item != 0:
                print(f"Warning, could not find {item} image to load.")

    return sprite_list