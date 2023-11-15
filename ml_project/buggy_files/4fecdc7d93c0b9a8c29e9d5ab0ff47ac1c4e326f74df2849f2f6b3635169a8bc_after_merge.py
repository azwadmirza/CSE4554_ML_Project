def to_int(s):
    # We must be able to handle octal representation for `mode` values notably
    if six.PY3 and re.match('^0[0-9]+$', s.strip()):
        s = '0o' + s[1:]
    try:
        return int(s, base=0)
    except ValueError:
        raise ValueError('"{}" is not a valid integer'.format(s))