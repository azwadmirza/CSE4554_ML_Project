def get_doc_size(svg):
    width = svg.get('width')
    height = svg.get('height')

    if width is None or height is None:
        # fall back to the dimensions from the viewBox
        viewbox = get_viewbox(svg)
        width = viewbox[2]
        height = viewbox[3]

    doc_width = convert_length(width)
    doc_height = convert_length(height)

    return doc_width, doc_height