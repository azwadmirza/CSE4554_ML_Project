def decode_output(output):
    if not isinstance(output, six.string_types):
        return output
    try:
        output = output.encode(DEFAULT_ENCODING)
    except (AttributeError, UnicodeDecodeError):
        if six.PY2:
            output = unicode.translate(vistir.misc.to_text(output),
                                            UNICODE_TO_ASCII_TRANSLATION_MAP)
        else:
            output = output.translate(UNICODE_TO_ASCII_TRANSLATION_MAP)
    output = output.decode(DEFAULT_ENCODING)
    return output