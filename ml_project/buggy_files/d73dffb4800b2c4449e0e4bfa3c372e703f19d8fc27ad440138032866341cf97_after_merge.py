def write_PN(fp, data_element, padding=b' ', encoding=None):
    if not encoding:
        encoding = [default_encoding] * 3

    if data_element.VM == 1:
        val = [data_element.value, ]
    else:
        val = data_element.value

    if isinstance(val[0], compat.text_type) or not in_py2:
        try:
            val = [elem.encode(encoding) for elem in val]
        except TypeError:
            val = [elem.encode(encoding[0]) for elem in val]

    val = b'\\'.join(val)

    if len(val) % 2 != 0:
        val = val + padding

    fp.write(val)