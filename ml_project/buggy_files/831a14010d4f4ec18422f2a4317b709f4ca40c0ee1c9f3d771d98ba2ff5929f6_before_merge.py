  def SetEnvironmentVariable(self, enviroment_variable):
    """Sets an environment variable.

    Args:
      enviroment_variable (EnvironmentVariableArtifact): environment variable
          artifact.
    """
    name = enviroment_variable.name.upper()
    self._environment_variables[name] = enviroment_variable