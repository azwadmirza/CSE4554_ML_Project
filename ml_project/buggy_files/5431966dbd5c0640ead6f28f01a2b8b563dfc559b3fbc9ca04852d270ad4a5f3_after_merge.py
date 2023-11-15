def subproc_arg_callback(_, match):
    """Check if match contains valid path"""
    text = match.group()
    try:
        ispath = os.path.exists(os.path.expanduser(text))
    except (FileNotFoundError, OSError):
        ispath = False
    yield (match.start(), Name.Constant if ispath else Text, text)