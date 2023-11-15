def read_multilayer_svg(
    filename: str, quantization: float, simplify: bool = False, return_size: bool = False
) -> Union["VectorData", Tuple["VectorData", float, float]]:
    """Read a multilayer SVG file and return its content as a :class:`VectorData` instance
    retaining the SVG's layer structure.

    Each top-level group is considered a layer. All non-group, top-level elements are imported
    in layer 1.

    Groups are matched to layer ID according their `inkscape:label` attribute, their `id`
    attribute or their appearing order, in that order of priority. Labels are stripped of
    non-numeric characters and the remaining is used as layer ID. Lacking numeric characters,
    the appearing order is used. If the label is 0, its changed to 1.

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

    vector_data = VectorData()

    # non-group top level elements are loaded in layer 1
    top_level_elements = doc.paths(group_filter=lambda x: x is doc.root)
    if top_level_elements:
        vector_data.add(
            _convert_flattened_paths(
                top_level_elements,
                quantization,
                scale_x,
                scale_y,
                offset_x,
                offset_y,
                simplify,
            ),
            1,
        )

    for i, g in enumerate(doc.root.iterfind("svg:g", svg.SVG_NAMESPACE)):
        # compute a decent layer ID
        lid_str = re.sub(
            "[^0-9]", "", g.get("{http://www.inkscape.org/namespaces/inkscape}label") or ""
        )
        if not lid_str:
            lid_str = re.sub("[^0-9]", "", g.get("id") or "")
        if lid_str:
            lid = int(lid_str)
            if lid == 0:
                lid = 1
        else:
            lid = i + 1

        vector_data.add(
            _convert_flattened_paths(
                doc.paths_from_group(g, g),
                quantization,
                scale_x,
                scale_y,
                offset_x,
                offset_y,
                simplify,
            ),
            lid,
        )

    if return_size:
        if width is None or height is None:
            _, _, width, height = vector_data.bounds() or 0, 0, 0, 0
        return vector_data, width, height
    else:
        return vector_data