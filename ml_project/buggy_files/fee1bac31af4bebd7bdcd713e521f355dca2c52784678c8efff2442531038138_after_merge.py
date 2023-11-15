def strip_esc_sequence(txt):
    '''
    Replace ESC (ASCII 27/Oct 33) to prevent unsafe strings
    from writing their own terminal manipulation commands
    '''
    if isinstance(txt, six.string_types):
        try:
            return txt.replace('\033', '?')
        except UnicodeDecodeError:
            return txt.replace(str('\033'), str('?'))  # future lint: disable=blacklisted-function
    else:
        return txt