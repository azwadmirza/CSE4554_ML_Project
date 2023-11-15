  def Parse(self, stat, _):
    """Parse the key currentcontrolset output."""
    value = stat.registry_data.GetValue()
    if not value:
      raise parsers.ParseError("Invalid value for key %s" % stat.pathspec.path)

    systemdrive = value[0:2]
    if re.match(r"^[A-Za-z]:$", systemdrive):
      yield rdfvalue.RDFString(systemdrive)
    else:
      raise parsers.ParseError("Bad drive letter for key %s" %
                               stat.pathspec.path)