def spoof_positions(obj):
    if not isinstance(obj, HyObject):
        return
    if not hasattr(obj, "start_column"):
        obj.start_column = 0
    if not hasattr(obj, "start_line"):
        obj.start_line = 0
    if (hasattr(obj, "__iter__") and
            not isinstance(obj, (string_types, bytes_type))):
        for x in obj:
            spoof_positions(x)