def _file_support_encoding(chars, file):
    encoding = getattr(file, "encoding", None)
    if encoding is not None:
        for char in chars:
            try:
                char.encode(encoding)
            except UnicodeEncodeError:
                break
        else:
            return True
    return False