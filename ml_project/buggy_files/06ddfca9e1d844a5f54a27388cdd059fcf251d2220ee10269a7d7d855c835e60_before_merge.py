  def Parse(self, stat, knowledge_base):
    """Parse the key currentcontrolset output."""
    value = stat.registry_data.GetValue()
    if not value:
      raise parsers.ParseError("Invalid value for key %s" % stat.pathspec.path)
    value = artifact_utils.ExpandWindowsEnvironmentVariables(value,
                                                             knowledge_base)
    if value:
      yield rdfvalue.RDFString(value)