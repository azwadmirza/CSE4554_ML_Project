def ansicolors_to_ptk1_names(stylemap):
    """Converts ansicolor names in a stylemap to old PTK1 color names
    """
    modified_stylemap = {}
    for token, style_str in stylemap.items():
        for color, ptk1_color in ANSICOLOR_NAMES_MAP.items():
            if ptk1_color not in style_str:
                style_str = style_str.replace(color, ptk1_color)
        modified_stylemap[token] = style_str
    return modified_stylemap