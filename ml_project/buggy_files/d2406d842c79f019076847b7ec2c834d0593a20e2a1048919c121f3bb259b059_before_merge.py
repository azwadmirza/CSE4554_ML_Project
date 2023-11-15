def decode_match(match):
    return codecs.decode(match.group(0), 'unicode_escape')