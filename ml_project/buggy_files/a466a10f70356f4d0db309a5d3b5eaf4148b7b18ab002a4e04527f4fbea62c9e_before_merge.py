def get_encodings():
    '''
    return a list of string encodings to try
    '''
    encodings = []
    loc = locale.getdefaultlocale()[-1]
    if loc:
        encodings.append(loc)
    encodings.append(sys.getdefaultencoding())
    encodings.extend(['utf-8', 'latin-1'])
    return encodings