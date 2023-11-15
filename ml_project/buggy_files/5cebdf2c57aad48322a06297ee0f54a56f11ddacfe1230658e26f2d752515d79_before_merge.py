def _text_or_file(input_):
    '''
    Determines if input is a path to a file, or a string with the
    content to be parsed.
    '''
    if os.path.isfile(input_):
        with salt.utils.files.fopen(input_) as fp_:
            return salt.utils.stringutils.to_bytes(fp_.read())
    else:
        return input_