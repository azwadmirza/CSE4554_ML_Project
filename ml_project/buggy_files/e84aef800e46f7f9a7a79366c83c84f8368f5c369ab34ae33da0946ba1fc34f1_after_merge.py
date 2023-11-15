def _get_pyvenv_cfg_lines():
    # type: () -> Optional[List[str]]
    """Reads {sys.prefix}/pyvenv.cfg and returns its contents as list of lines

    Returns None, if it could not read/access the file.
    """
    pyvenv_cfg_file = os.path.join(sys.prefix, 'pyvenv.cfg')
    try:
        # Although PEP 405 does not specify, the built-in venv module always
        # writes with UTF-8. (pypa/pip#8717)
        with io.open(pyvenv_cfg_file, encoding='utf-8') as f:
            return f.read().splitlines()  # avoids trailing newlines
    except IOError:
        return None