def mangle(s):
    """Stringify the argument and convert it to a valid Python identifier
    according to Hy's mangling rules."""
    def unicode_char_to_hex(uchr):
        # Covert a unicode char to hex string, without prefix
        return uchr.encode('unicode-escape').decode('utf-8').lstrip('\\U').lstrip('\\u').lstrip('0')

    assert s

    s = str_type(s)
    s = s.replace("-", "_")
    s2 = s.lstrip('_')
    leading_underscores = '_' * (len(s) - len(s2))
    s = s2

    if s.endswith("?"):
        s = 'is_' + s[:-1]
    if not isidentifier(leading_underscores + s):
        # Replace illegal characters with their Unicode character
        # names, or hexadecimal if they don't have one.
        s = 'hyx_' + ''.join(
            c
               if c != mangle_delim and isidentifier('S' + c)
                 # We prepend the "S" because some characters aren't
                 # allowed at the start of an identifier.
               else '{0}{1}{0}'.format(mangle_delim,
                   unicodedata.name(c, '').lower().replace('-', 'H').replace(' ', '_')
                   or 'U{}'.format(unicode_char_to_hex(c)))
            for c in unicode_to_ucs4iter(s))

    s = leading_underscores + s
    assert isidentifier(s)
    return s