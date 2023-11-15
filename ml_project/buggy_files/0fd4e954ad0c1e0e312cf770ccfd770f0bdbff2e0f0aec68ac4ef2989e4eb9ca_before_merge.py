def is_dir_writable(path):
    """
    Checks if the directory is writable. Creates the directory if one does not exist.
    :param path: absolute path of directory
    :return: True if writable, False otherwise
    """
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        open(os.path.join(path, 'temp'), 'w')
    except IOError as io_error:
        return False, io_error
    except OSError as os_error:
        return False, os_error
    else:
        os.remove(os.path.join(path, 'temp'))
        return True, None