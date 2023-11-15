def latinify(string, default="?", pure_ascii=False):
    """
    Convert a unicode string to "safe" ascii/latin-1 characters.
    This is used as a last resort when normal encoding does not work.

    Arguments:
        string (str): A string to convert to 'safe characters' convertable
            to an latin-1 bytestring later.
        default (str, optional): Characters resisting mapping will be replaced
            with this character or string. The intent is to apply an encode operation
            on the string soon after.

    Returns:
        string (str): A 'latinified' string where each unicode character has been
            replaced with a 'safe' equivalent available in the ascii/latin-1 charset.
    Notes:
        This is inspired by the gist by Ricardo Murri:
            https://gist.github.com/riccardomurri/3c3ccec30f037be174d3

    """

    from unicodedata import name

    if isinstance(string, bytes):
        string = string.decode("utf8")

    converted = []
    for unich in iter(string):
        try:
            ch = unich.encode("utf8").decode("ascii")
        except UnicodeDecodeError:
            # deduce a latin letter equivalent from the Unicode data
            # point name; e.g., since `name(u'á') == 'LATIN SMALL
            # LETTER A WITH ACUTE'` translate `á` to `a`.  However, in
            # some cases the unicode name is still "LATIN LETTER"
            # although no direct equivalent in the Latin alphabet
            # exists (e.g., Þ, "LATIN CAPITAL LETTER THORN") -- we can
            # avoid these cases by checking that the letter name is
            # composed of one letter only.
            # We also supply some direct-translations for some particular
            # common cases.
            what = name(unich)
            if what in _UNICODE_MAP:
                ch = _UNICODE_MAP[what]
            else:
                what = what.split()
                if what[0] == "LATIN" and what[2] == "LETTER" and len(what[3]) == 1:
                    ch = what[3].lower() if what[1] == "SMALL" else what[3].upper()
                else:
                    ch = default
        converted.append(chr(ord(ch)))
    return "".join(converted)