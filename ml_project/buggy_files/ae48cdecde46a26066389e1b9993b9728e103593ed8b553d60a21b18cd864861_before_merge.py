def write(text, filename, encoding='utf-8', mode='wb'):
    """
    Write 'text' to file ('filename') assuming 'encoding' in an atomic way
    Return (eventually new) encoding
    """
    text, encoding = encode(text, encoding)
    if 'a' in mode:
        with open(filename, mode) as textfile:
            textfile.write(text)
    else:
        # Based in the solution at untitaker/python-atomicwrites#42.
        # Needed to fix file permissions overwritting.
        # See spyder-ide/spyder#9381.
        try:
            original_mode = os.stat(filename).st_mode
        except OSError:  # Change to FileNotFoundError for PY3
            # Creating a new file, emulate what os.open() does
            umask = os.umask(0)
            os.umask(umask)
            original_mode = 0o777 & ~umask
        with atomic_write(filename,
                          overwrite=True,
                          mode=mode) as textfile:
            textfile.write(text)
        os.chmod(filename, original_mode)
    return encoding