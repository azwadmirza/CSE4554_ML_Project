def sanitize_foldername(name):
    """Return foldername with dodgy chars converted to safe ones
    Remove any leading and trailing dot and space characters
    """
    if not name:
        return name

    illegal = CH_ILLEGAL + ':"'
    legal = CH_LEGAL + "-'"

    if sabnzbd.WIN32 or sabnzbd.cfg.sanitize_safe():
        # Remove all bad Windows chars too
        illegal += CH_ILLEGAL_WIN
        legal += CH_LEGAL_WIN

    repl = sabnzbd.cfg.replace_illegal()
    lst = []
    for ch in name.strip():
        if ch in illegal:
            if repl:
                ch = legal[illegal.find(ch)]
                lst.append(ch)
        else:
            lst.append(ch)
    name = "".join(lst)
    name = name.strip()

    if sabnzbd.WIN32 or sabnzbd.cfg.sanitize_safe():
        name = replace_win_devices(name)

    # And finally, make sure it doesn't end in a dot
    if name != "." and name != "..":
        name = name.rstrip(".")
    if not name:
        name = "unknown"

    return name