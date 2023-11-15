  def Parse(self, stat, knowledge_base):
    """Expand any variables in the value."""
    value = stat.registry_data.GetValue()
    if not value:
      raise parsers.ParseError("Invalid value for key %s" % stat.pathspec.path)
    value = artifact_utils.ExpandWindowsEnvironmentVariables(value,
                                                             knowledge_base)
    if value:
      yield rdfvalue.RDFString(value)