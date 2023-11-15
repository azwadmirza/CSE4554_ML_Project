def xml_escape(value):
    if not isinstance(value, (str, bytes)):
        value = str(value)
    if not isinstance(value, str):
        value = value.decode('utf-8')
    return xmltools_escape(value)