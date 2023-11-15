def _partial_color_tokenize_main(template, styles):
    formatter = string.Formatter()
    bopen = '{'
    bclose = '}'
    colon = ':'
    expl = '!'
    color = Color.NO_COLOR
    fg = bg = None
    value = ''
    toks = []
    for literal, field, spec, conv in formatter.parse(template):
        if field is None:
            value += literal
        elif field in KNOWN_COLORS or '#' in field:
            value += literal
            next_color, fg, bg = color_by_name(field, fg, bg)
            if next_color is not color:
                if len(value) > 0:
                    toks.append((color, value))
                    if styles is not None:
                        styles[color]  # ensure color is available
                color = next_color
                value = ''
        elif field is not None:
            parts = [literal, bopen, field]
            if conv is not None and len(conv) > 0:
                parts.append(expl)
                parts.append(conv)
            if spec is not None and len(spec) > 0:
                parts.append(colon)
                parts.append(spec)
            parts.append(bclose)
            value += ''.join(parts)
        else:
            value += literal
    toks.append((color, value))
    return toks, color