def _wrap_gzip(fileobj, mode):
    return contextlib.closing(gzip.GzipFile(fileobj=fileobj, mode=mode))