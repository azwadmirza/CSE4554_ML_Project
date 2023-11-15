def read_svg(
    filename: str, quantization: float, simplify: bool = False, return_size: bool = False
) -> Union["LineCollection", Tuple["LineCollection", float, float]]:
    """Read a SVG file an return its content as a :class:`LineCollection` instance.

    All curved geometries are chopped in segments no longer than the value of *quantization*.
    Optionally, the geometries are simplified using Shapely, using the value of *quantization*
    as tolerance.

    Args:
        filename: path of the SVG file
        quantization: maximum size of segment used to approximate curved geometries
        simplify: run Shapely's simplify on loaded geometry
        return_size: if True, return a size 3 Tuple containing the geometries and the SVG
            width and height

    Returns:
        imported geometries, and optionally width and height of the SVG
    """

    doc = svg.Document(filename)
    width, height, scale_x, scale_y, offset_x, offset_y = _calculate_page_size(doc.root)
    lc = _convert_flattened_paths(
        doc.flatten_all_paths(), quantization, scale_x, scale_y, offset_x, offset_y, simplify,
    )

    if return_size:
        if width is None or height is None:
            _, _, width, height = lc.bounds() or 0, 0, 0, 0
        return lc, width, height
    else:
        return lc