def to_text(value, encoding="utf-8"):
    if isinstance(value, six.binary_type):
        return value.decode(encoding)
    if isinstance(value, six.integer_types):
        return six.text_type(value)
    assert isinstance(value, six.text_type)
    return value