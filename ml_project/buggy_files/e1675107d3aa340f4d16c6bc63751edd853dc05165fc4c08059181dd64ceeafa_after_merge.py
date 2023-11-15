def validate_markers(instance, attr_, value):
    from packaging.markers import Marker, InvalidMarker
    try:
        Marker("{0}{1}".format(attr_.name, value))
    except InvalidMarker:
        raise ValueError("Invalid Marker {0}{1}".format(attr_, value))