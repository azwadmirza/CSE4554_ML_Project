  def SetEnvironmentVariable(self, environment_variable):
    """Sets an environment variable.

    Args:
      environment_variable (EnvironmentVariableArtifact): environment variable
          artifact.
    """
    name = environment_variable.name.upper()
    self._environment_variables[name] = environment_variable