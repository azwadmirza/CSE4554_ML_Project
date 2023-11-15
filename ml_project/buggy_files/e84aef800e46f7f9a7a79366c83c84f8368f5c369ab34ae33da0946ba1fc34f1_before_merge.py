def _get_pyvenv_cfg_lines():
    # type: () -> Optional[List[str]]
    """Reads {sys.prefix}/pyvenv.cfg and returns its contents as list of lines

    Returns None, if it could not read/access the file.
    """
    pyvenv_cfg_file = os.path.join(sys.prefix, 'pyvenv.cfg')
    try:
        with open(pyvenv_cfg_file) as f:
            return f.read().splitlines()  # avoids trailing newlines
    except IOError:
        return None