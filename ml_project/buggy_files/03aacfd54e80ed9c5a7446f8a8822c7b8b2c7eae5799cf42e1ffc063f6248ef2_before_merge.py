def select(layer, event):
    """Select shapes or vertices either in select or direct select mode.

    Once selected shapes can be moved or resized, and vertices can be moved
    depending on the mode. Holding shift when resizing a shape will preserve
    the aspect ratio.
    """
    shift = 'Shift' in event.modifiers
    # on press
    layer._moving_value = copy(layer._value)
    shape_under_cursor, vertex_under_cursor = layer._value
    if vertex_under_cursor is None:
        if shift and shape_under_cursor is not None:
            if shape_under_cursor in layer.selected_data:
                layer.selected_data.remove(shape_under_cursor)
                shapes = layer.selected_data
                layer._selected_box = layer.interaction_box(shapes)
            else:
                layer.selected_data.append(shape_under_cursor)
                shapes = layer.selected_data
                layer._selected_box = layer.interaction_box(shapes)
        elif shape_under_cursor is not None:
            if shape_under_cursor not in layer.selected_data:
                layer.selected_data = {shape_under_cursor}
        else:
            layer.selected_data = set()
    layer._set_highlight()
    yield

    # on move
    while event.type == 'mouse_move':
        # Drag any selected shapes
        layer._move(layer.displayed_coordinates)
        yield

    # on release
    shift = 'Shift' in event.modifiers
    if not layer._is_moving and not layer._is_selecting and not shift:
        if shape_under_cursor is not None:
            layer.selected_data = {shape_under_cursor}
        else:
            layer.selected_data = set()
    elif layer._is_selecting:
        layer.selected_data = layer._data_view.shapes_in_box(layer._drag_box)
        layer._is_selecting = False
        layer._set_highlight()
    layer._is_moving = False
    layer._drag_start = None
    layer._drag_box = None
    layer._fixed_vertex = None
    layer._moving_value = (None, None)
    layer._set_highlight()
    layer._update_thumbnail()