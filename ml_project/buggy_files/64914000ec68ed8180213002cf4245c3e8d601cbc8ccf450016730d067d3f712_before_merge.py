def replace_prefix(mode, data, placeholder, new_prefix):
    if mode is FileMode.text:
        data = data.replace(placeholder.encode(UTF8), new_prefix.encode(UTF8))
    elif mode == FileMode.binary:
        data = binary_replace(data, placeholder.encode(UTF8), new_prefix.encode(UTF8))
    else:
        raise RuntimeError("Invalid mode: %r" % mode)
    return data