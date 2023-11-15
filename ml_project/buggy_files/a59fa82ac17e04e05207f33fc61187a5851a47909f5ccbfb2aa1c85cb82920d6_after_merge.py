def get_state(path):
    ''' Find out current state '''

    b_path = to_bytes(path, errors='surrogate_or_strict')
    try:
        if os.path.lexists(b_path):
            if os.path.islink(b_path):
                return 'link'
            elif os.path.isdir(b_path):
                return 'directory'
            elif os.stat(b_path).st_nlink > 1:
                return 'hard'

            # could be many other things, but defaulting to file
            return 'file'

        return 'absent'
    except OSError as e:
        if e.errno == errno.ENOENT:  # It may already have been removed
            return 'absent'
        else:
            raise