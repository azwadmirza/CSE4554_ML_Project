def compute_md5sum(file_full_path):
    if not isfile(file_full_path):
        raise FileNotFoundError(file_full_path)

    hash_md5 = hashlib.md5()
    with open(file_full_path, "rb") as fh:
        for chunk in iter(partial(fh.read, 8192), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()