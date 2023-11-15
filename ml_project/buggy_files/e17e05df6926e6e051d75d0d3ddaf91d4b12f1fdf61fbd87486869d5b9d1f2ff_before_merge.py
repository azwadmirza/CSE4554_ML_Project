def open_zip(path, *args, **kwargs):
  """A contextmanager for zip files.  Passes through positional and kwargs to zipfile.ZipFile."""
  with contextlib.closing(zipfile.ZipFile(path, *args, **kwargs)) as zip:
    yield zip