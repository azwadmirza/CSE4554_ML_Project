def ansi_color_escape_code_to_name(escape_code, style, reversed_style=None):
    """Converts an ASNI color code escape sequence to a tuple of color names
    in the provided style ('default' should almost be the style). For example,
    '0' becomes ('NO_COLOR',) and '32;41' becomes ('GREEN', 'BACKGROUND_RED').
    The style keyword may either be a string, in which the style is looked up,
    or an actual style dict.  You can also provide a reversed style mapping,
    too, which is just the keys/values of the style dict swapped. If reversed
    style is not provided, it is computed.
    """
    key = (escape_code, style)
    if key in _ANSI_COLOR_ESCAPE_CODE_TO_NAME_CACHE:
        return _ANSI_COLOR_ESCAPE_CODE_TO_NAME_CACHE[key]
    if reversed_style is None:
        style, reversed_style = ansi_reverse_style(style, return_style=True)
    # strip some actual escape codes, if needed.
    match = ANSI_ESCAPE_CODE_RE.match(escape_code)
    if not match:
        msg = 'Invalid ANSI color sequence "{0}", using "NO_COLOR" instead.'.format(
            escape_code
        )
        warnings.warn(msg, RuntimeWarning)
        return ("NO_COLOR",)
    ec = match.group(2)
    names = []
    n_ints = 0
    seen_set_foreback = False
    for e in ec.split(";"):
        no_left_zero = e.lstrip("0") if len(e) > 1 else e
        if seen_set_foreback and n_ints > 0:
            names.append(e)
            n_ints -= 1
            if n_ints == 0:
                seen_set_foreback = False
            continue
        else:
            names.append(reversed_style.get(no_left_zero, no_left_zero))
        # set the flags for next time
        if "38" == e or "48" == e:
            seen_set_foreback = True
        elif seen_set_foreback and "2" == e:
            n_ints = 3
        elif seen_set_foreback and "5" == e:
            n_ints = 1
    # normalize names
    n = ""
    norm_names = []
    prefixes = ""
    for name in names:
        if name == "NO_COLOR":
            # skip most '0' entries
            continue
        elif "BACKGROUND_" in name and n:
            prefixes += n
            n = ""
        n = n + name if n else name
        if n.endswith("_"):
            continue
        elif ANSI_COLOR_NAME_SET_SHORT_RE.match(n) is not None:
            pre, fore_back, short = ANSI_COLOR_NAME_SET_SHORT_RE.match(n).groups()
            n = _color_name_from_ints(
                short_to_ints(short), background=(fore_back == "BACK"), prefix=pre
            )
        elif ANSI_COLOR_NAME_SET_3INTS_RE.match(n) is not None:
            pre, fore_back, r, g, b = ANSI_COLOR_NAME_SET_3INTS_RE.match(n).groups()
            n = _color_name_from_ints(
                (int(r), int(g), int(b)), background=(fore_back == "BACK"), prefix=pre
            )
        elif "GROUND_FAINT_" in n:
            # have 1 or 2, but not 3 ints
            n += "_"
            continue
        # error check
        if not iscolor(n):
            msg = (
                "Could not translate ANSI color code {escape_code!r} "
                "into a known color in the palette. Specifically, the {n!r} "
                "portion of {name!r} in {names!r} seems to missing."
            )
            raise ValueError(
                msg.format(escape_code=escape_code, names=names, name=name, n=n)
            )
        norm_names.append(n)
        n = ""
    # check if we have pre- & post-fixes to apply to the last, non-background element
    prefixes += n
    if prefixes.endswith("_"):
        for i in range(-1, -len(norm_names) - 1, -1):
            if "BACKGROUND_" not in norm_names[i]:
                norm_names[i] = prefixes + norm_names[i]
                break
        else:
            # only have background colors, so select WHITE as default color
            norm_names.append(prefixes + "WHITE")
    # return
    if len(norm_names) == 0:
        return ("NO_COLOR",)
    else:
        return tuple(norm_names)