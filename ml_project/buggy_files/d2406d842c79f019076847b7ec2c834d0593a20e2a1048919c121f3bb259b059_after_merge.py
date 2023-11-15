def decode_match(match):
    try:
        return codecs.decode(match.group(0), 'unicode_escape')
    except UnicodeDecodeError as err:
        raise MesonUnicodeDecodeError(match.group(0))