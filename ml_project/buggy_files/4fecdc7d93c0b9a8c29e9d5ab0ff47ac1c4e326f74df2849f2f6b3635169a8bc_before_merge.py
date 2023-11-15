def to_int(s):
    # We must be able to handle octal representation for `mode` values notably
    if six.PY3 and re.match('^0[0-9]+$', s.strip()):
        s = '0o' + s[1:]
    return int(s, base=0)