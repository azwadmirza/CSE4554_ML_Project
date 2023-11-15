def to_binary(value, encoding="utf-8"):
    if isinstance(value, six.text_type):
        return value.encode(encoding)
    if isinstance(value, six.integer_types):
        return six.binary_type(value)
    assert isinstance(value, six.binary_type)
    return value