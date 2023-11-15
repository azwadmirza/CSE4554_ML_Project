def _normpath(path):
  path = os.path.normpath(path)
  if path.startswith('.') or os.path.isabs(path):
    raise UnsafeArchiveError('Archive at %s is not safe.' % path)
  if path.endswith('~') or os.path.basename(path).startswith('.'):
    return None
  return path