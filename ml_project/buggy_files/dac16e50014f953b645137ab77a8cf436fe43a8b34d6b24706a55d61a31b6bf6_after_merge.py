def sanitize_filename(filename):
    """
    Remove specific characters from the provided ``filename``.
    :param filename: The filename to clean
    :return: The cleaned ``filename``
    """

    if isinstance(filename, (str, text_type)):
        # https://stackoverflow.com/a/31976060/7597273
        remove = r''.join((
            r':"<>|?',
            r'™',  # Trade Mark Sign [unicode: \u2122]
            r'\t',  # Tab
            r'\x00-\x1f',  # Null & Control characters
        ))
        remove = r'[' + remove + r']'

        filename = re.sub(r'[\\/\*]', '-', filename)
        filename = re.sub(remove, '', filename)
        # Filenames cannot end in a space or dot on Windows systems
        filename = filename.strip(' .')

        return filename

    return ''