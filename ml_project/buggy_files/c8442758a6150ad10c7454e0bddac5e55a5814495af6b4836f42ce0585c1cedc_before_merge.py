  def can_add(self, dist):
    filename, ext = os.path.splitext(os.path.basename(dist.location))
    if ext.lower() != '.whl':
      # This supports resolving pex's own vendored distributions which are vendored in directory
      # directory with the project name (`pip/` for pip) and not the corresponding wheel name
      # (`pip-19.3.1-py2.py3-none-any.whl/` for pip). Pex only vendors universal wheels for all
      # platforms it supports at buildtime and runtime so this is always safe.
      return True

    try:
      wheel_name_, wheel_raw_version_, wheel_tags = filename.split('-', 2)
    except ValueError:
      return False

    if self._supported_tags.isdisjoint(tags.parse_tag(wheel_tags)):
      return False

    python_requires = dist_metadata.requires_python(dist)
    if not python_requires:
      return True

    return self._interpreter.identity.version_str in python_requires