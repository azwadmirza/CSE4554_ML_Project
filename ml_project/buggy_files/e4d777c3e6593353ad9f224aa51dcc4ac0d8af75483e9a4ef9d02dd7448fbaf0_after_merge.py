def _normpath(path):
  path = os.path.normpath(path)
  if (path.startswith('.')
      or os.path.isabs(path)
      or path.endswith('~')
      or os.path.basename(path).startswith('.')):
    return None
  return path