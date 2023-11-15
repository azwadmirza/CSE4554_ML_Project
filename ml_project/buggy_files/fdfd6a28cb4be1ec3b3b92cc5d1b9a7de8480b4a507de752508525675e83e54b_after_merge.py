def _get_color_indexes(style_map):
    """ Generates the color and windows color index for a style """
    import prompt_toolkit
    table = prompt_toolkit.terminal.win32_output.ColorLookupTable()
    pt_style = prompt_toolkit.styles.style_from_dict(style_map)
    for token in style_map:
        attr = pt_style.token_to_attrs[token]
        if attr.color is not None:
            try:
                index = table.lookup_color(attr.color, attr.bgcolor)
            except AttributeError:
                index = table.lookup_fg_color(attr.color)
            try:
                rgb = (int(attr.color[0:2], 16),
                       int(attr.color[2:4], 16),
                       int(attr.color[4:6], 16))
            except Exception:
                rgb = None
            yield token, index, rgb