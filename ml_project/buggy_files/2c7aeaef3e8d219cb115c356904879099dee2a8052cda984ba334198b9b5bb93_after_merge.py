def get_commands_from_metadata(image_layer):
    """Given the image layer object, get the list of command objects that
    created the layer. Return an empty list of we can't do that"""
    # set up notice origin for the layer
    origin_layer = 'Layer {}'.format(image_layer.layer_index)
    # check if there is a key containing the script that created the layer
    if image_layer.created_by:
        command_line = fltr.get_run_command(image_layer.created_by)
        if command_line:
            command_list, msg = fltr.filter_install_commands(
                general.clean_command(command_line))
            if msg:
                image_layer.origins.add_notice_to_origins(
                    origin_layer, Notice(msg, 'warning'))
            return command_list
    image_layer.origins.add_notice_to_origins(
        origin_layer, Notice(errors.no_layer_created_by, 'warning'))
    return []