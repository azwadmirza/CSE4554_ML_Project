def decode_output(output):
    if not isinstance(output, six.string_types):
        return output
    try:
        output = output.encode(DEFAULT_ENCODING)
    except (AttributeError, UnicodeDecodeError, UnicodeEncodeError):
        if six.PY2:
            output = unicode.translate(vistir.misc.to_text(output),
                                            UNICODE_TO_ASCII_TRANSLATION_MAP)
        else:
            output = output.translate(UNICODE_TO_ASCII_TRANSLATION_MAP)
        output = output.encode(DEFAULT_ENCODING, "replace")
    return vistir.misc.to_text(output, encoding=DEFAULT_ENCODING, errors="replace")
    return output