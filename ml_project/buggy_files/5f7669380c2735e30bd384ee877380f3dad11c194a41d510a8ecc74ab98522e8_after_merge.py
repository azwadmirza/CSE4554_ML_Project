  def Parse(self, stat, _):
    """Parse the key currentcontrolset output."""
    # SystemDriveEnvironmentVariable produces a statentry,
    # WindowsEnvironmentVariableSystemDrive produces a string
    if isinstance(stat, rdf_client.StatEntry):
      value = stat.registry_data.GetValue()
    elif isinstance(stat, rdfvalue.RDFString):
      value = stat
    if not value:
      raise parsers.ParseError("Invalid value for key %s" % stat.pathspec.path)

    systemdrive = value[0:2]
    if re.match(r"^[A-Za-z]:$", systemdrive):
      yield rdfvalue.RDFString(systemdrive)
    else:
      raise parsers.ParseError("Bad drive letter for key %s" %
                               stat.pathspec.path)