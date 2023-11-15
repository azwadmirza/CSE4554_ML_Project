def get_doc_size(svg):
    width = svg.get('width')
    height = svg.get('height')

    if width == "100%" and height == "100%":
        # Some SVG editors set width and height to "100%".  I can't find any
        # solid documentation on how one is supposed to interpret that, so
        # just ignore it and use the viewBox.  That seems to have the intended
        # result anyway.

        width = None
        height = None

    if width is None or height is None:
        # fall back to the dimensions from the viewBox
        viewbox = get_viewbox(svg)
        width = viewbox[2]
        height = viewbox[3]

    doc_width = convert_length(width)
    doc_height = convert_length(height)

    return doc_width, doc_height