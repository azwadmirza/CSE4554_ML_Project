def get_commands_from_history(image_layer):
    '''Given the image layer object and the shell, get the list of command
    objects that created the layer'''
    # set up notice origin for the layer
    origin_layer = 'Layer: ' + image_layer.fs_hash[:10]
    if image_layer.created_by:
        instruction = created_to_instruction(image_layer.created_by)
        image_layer.origins.add_notice_to_origins(origin_layer, Notice(
            formats.dockerfile_line.format(dockerfile_instruction=instruction),
            'info'))
    else:
        image_layer.origins.add_notice_to_origins(origin_layer, Notice(
            formats.no_created_by, 'warning'))
    command_line = instruction.split(' ', 1)[1]
    # Image layers are created with the directives RUN, ADD and COPY
    # For ADD and COPY instructions, there is no information about the
    # packages added
    if 'ADD' in instruction or 'COPY' in instruction:
        image_layer.origins.add_notice_to_origins(origin_layer, Notice(
            errors.unknown_content.format(files=command_line), 'warning'))
        # return an empty list as we cannot find any commands
        return []
    # for RUN instructions we can return a list of commands
    command_list, msg = common.filter_install_commands(command_line)
    if msg:
        image_layer.origins.add_notice_to_origins(origin_layer, Notice(
            msg, 'warning'))
    return command_list