def to_text(value, encoding="utf-8"):
    if isinstance(value, (six.string_types, six.binary_type)):
        return value.decode(encoding)
    if isinstance(value, int):
        return six.text_type(value)
    assert isinstance(value, six.text_type)
    return value