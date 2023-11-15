def split_markers_from_line(line):
    """Split markers from a dependency"""
    from packaging.markers import Marker, InvalidMarker
    if not any(line.startswith(uri_prefix) for uri_prefix in SCHEME_LIST):
        marker_sep = ";"
    else:
        marker_sep = "; "
    markers = None
    if marker_sep in line:
        line, markers = line.split(marker_sep, 1)
        markers = markers.strip() if markers else None
    return line, markers