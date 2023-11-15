def rgb_to_256(rgb):
    """Find the closest ANSI 256 approximation to the given RGB value.

        >>> rgb2short('123456')
        ('23', '005f5f')
        >>> rgb2short('ffffff')
        ('231', 'ffffff')
        >>> rgb2short('0DADD6') # vimeo logo
        ('38', '00afd7')

    Parameters
    ----------
    rgb : Hex code representing an RGB value, eg, 'abcdef'

    Returns
    -------
    String between 0 and 255, compatible with xterm.
    """
    rgb = rgb.lstrip("#")
    if len(rgb) == 0:
        return "0", "000000"
    incs = (0x00, 0x5f, 0x87, 0xaf, 0xd7, 0xff)
    # Break 6-char RGB code into 3 integer vals.
    parts = rgb_to_ints(rgb)
    res = []
    for part in parts:
        i = 0
        while i < len(incs) - 1:
            s, b = incs[i], incs[i + 1]  # smaller, bigger
            if s <= part <= b:
                s1 = abs(s - part)
                b1 = abs(b - part)
                if s1 < b1:
                    closest = s
                else:
                    closest = b
                res.append(closest)
                break
            i += 1
    res = "".join([("%02.x" % i) for i in res])
    equiv = RGB_TO_SHORT[res]
    return equiv, res