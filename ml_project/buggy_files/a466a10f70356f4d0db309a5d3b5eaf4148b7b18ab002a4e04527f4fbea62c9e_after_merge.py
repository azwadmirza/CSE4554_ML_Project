def get_encodings():
    '''
    return a list of string encodings to try
    '''
    encodings = []

    try:
        loc_enc = locale.getdefaultlocale()[-1]
    except (ValueError, IndexError):  # system locale is nonstandard or malformed
        loc_enc = None
    if loc_enc:
        encodings.append(loc_enc)

    try:
        enc = sys.getdefaultencoding()
    except ValueError:  # system encoding is nonstandard or malformed
        enc = None
    if enc:
        encodings.append(enc)

    encodings.extend(['utf-8', 'latin-1'])
    return encodings