def _wrap_gzip(fileobj, mode):
    return gzip.GzipFile(fileobj=fileobj, mode=mode)