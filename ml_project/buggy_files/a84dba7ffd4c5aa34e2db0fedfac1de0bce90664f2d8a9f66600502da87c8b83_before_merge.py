def sanitize(s):
    if s:
        return re.sub(r"""[&\\\<\>"'%();+]""", "", s)
    else:
        return s