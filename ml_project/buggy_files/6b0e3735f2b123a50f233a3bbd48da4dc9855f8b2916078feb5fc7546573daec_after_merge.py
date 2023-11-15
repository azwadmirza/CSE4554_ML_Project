  def from_string(cls, requirement_string, options_builder, interpreter=None):
    requirement_string, extras = strip_extras(requirement_string)
    if cls.is_installable(requirement_string):
      if interpreter is None:
        raise cls.InvalidRequirement('%s is not an installable directory because we were called '
                                     'without an interpreter to use to execute setup.py.'
                                     % requirement_string)
      packager = Packager(requirement_string, interpreter=interpreter)
      try:
        sdist = packager.sdist()
      except SetuptoolsInstallerBase.Error:
        raise cls.InvalidRequirement('Could not create source distribution for %s'
                                     % requirement_string)
      package = Package.from_href(sdist)
      return ResolvablePackage(package, options_builder.build(package.name), extras=extras)
    else:
      raise cls.InvalidRequirement('%s does not appear to be an installable directory.'
                                   % requirement_string)