def subproc_arg_callback(_, match):
    """Check if match contains valid path"""
    text = match.group()
    yield (match.start(),
           Name.Constant if os.path.exists(os.path.expanduser(text)) else Text,
           text)