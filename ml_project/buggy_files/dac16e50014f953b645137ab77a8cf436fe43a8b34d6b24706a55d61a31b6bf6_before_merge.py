def sanitize_filename(filename):
    """
    Remove specific characters from the provided ``filename``.
    :param filename: The filename to clean
    :return: The ``filename``cleaned
    """

    if isinstance(filename, (str, text_type)):
        filename = re.sub(r'[\\/\*]', '-', filename)
        filename = re.sub(r'[:"<>|?]', '', filename)
        filename = re.sub(r'™', '', filename)  # Trade Mark Sign unicode: \u2122
        filename = filename.strip(' .')

        return filename

    return ''