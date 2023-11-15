def get_encoding(path):
    '''
    Detect a file's encoding using the following:
    - Check for ascii
    - Check for Byte Order Marks (BOM)
    - Check for UTF-8 Markers
    - Check System Encoding

    Args:

        path (str): The path to the file to check

    Returns:
        str: The encoding of the file

    Raises:
        CommandExecutionError: If the encoding cannot be detected
    '''
    def check_ascii(_data):
        # If all characters can be decoded to ASCII, then it's ASCII
        try:
            _data.decode('ASCII')
            log.debug('Found ASCII')
        except UnicodeDecodeError:
            return False
        else:
            return True

    def check_bom(_data):
        # Supported Python Codecs
        # https://docs.python.org/2/library/codecs.html
        # https://docs.python.org/3/library/codecs.html
        boms = [
            ('UTF-32-BE', salt.utils.stringutils.to_bytes(codecs.BOM_UTF32_BE)),
            ('UTF-32-LE', salt.utils.stringutils.to_bytes(codecs.BOM_UTF32_LE)),
            ('UTF-16-BE', salt.utils.stringutils.to_bytes(codecs.BOM_UTF16_BE)),
            ('UTF-16-LE', salt.utils.stringutils.to_bytes(codecs.BOM_UTF16_LE)),
            ('UTF-8', salt.utils.stringutils.to_bytes(codecs.BOM_UTF8)),
            ('UTF-7', salt.utils.stringutils.to_bytes('\x2b\x2f\x76\x38\x2D')),
            ('UTF-7', salt.utils.stringutils.to_bytes('\x2b\x2f\x76\x38')),
            ('UTF-7', salt.utils.stringutils.to_bytes('\x2b\x2f\x76\x39')),
            ('UTF-7', salt.utils.stringutils.to_bytes('\x2b\x2f\x76\x2b')),
            ('UTF-7', salt.utils.stringutils.to_bytes('\x2b\x2f\x76\x2f')),
        ]
        for _encoding, bom in boms:
            if _data.startswith(bom):
                log.debug('Found BOM for %s', _encoding)
                return _encoding
        return False

    def check_utf8_markers(_data):
        try:
            decoded = _data.decode('UTF-8')
        except UnicodeDecodeError:
            return False
        else:
            # Reject surrogate characters in Py2 (Py3 behavior)
            if six.PY2:
                for char in decoded:
                    if 0xD800 <= ord(char) <= 0xDFFF:
                        return False
            return True

    def check_system_encoding(_data):
        try:
            _data.decode(__salt_system_encoding__)
        except UnicodeDecodeError:
            return False
        else:
            return True

    if not os.path.isfile(path):
        raise CommandExecutionError('Not a file')
    try:
        with fopen(path, 'rb') as fp_:
            data = fp_.read(2048)
    except os.error:
        raise CommandExecutionError('Failed to open file')

    # Check for ASCII first
    if check_ascii(data):
        return 'ASCII'

    # Check for Unicode BOM
    encoding = check_bom(data)
    if encoding:
        return encoding

    # Check for UTF-8 markers
    if check_utf8_markers(data):
        return 'UTF-8'

    # Check system encoding
    if check_system_encoding(data):
        return __salt_system_encoding__

    raise CommandExecutionError('Could not detect file encoding')