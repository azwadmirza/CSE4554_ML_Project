def xml_escape(value):
    if not isinstance(value, (str, bytes)):
        value = str(value)
    if not isinstance(value, str):
        value = value.decode('utf-8')
    value = xmltools_escape(value)
    return value.encode('utf-8')