def sanitize(s):
    if s:
        return re.escape(s)
    else:
        return s