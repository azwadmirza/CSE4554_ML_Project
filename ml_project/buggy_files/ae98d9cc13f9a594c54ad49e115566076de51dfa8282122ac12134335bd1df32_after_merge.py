def load_object(file_path):
    file_path = os.path.expanduser(file_path)
    # reading to string and loads is 2.5x faster that using the file handle and load.
    try:
        with open(file_path, 'rb') as fh:
            return pickle.load(fh, encoding='bytes')
    except pickle.UnpicklingError as e:
        raise ValueError from e