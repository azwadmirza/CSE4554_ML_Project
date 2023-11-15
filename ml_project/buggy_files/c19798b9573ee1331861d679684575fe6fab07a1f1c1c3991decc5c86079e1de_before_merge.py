  def __init__(self, pex, pex_info, interpreter=None, **kw):
    self._internal_cache = os.path.join(pex, pex_info.internal_cache)
    self._pex = pex
    self._pex_info = pex_info
    self._activated = False
    self._working_set = None
    self._interpreter = interpreter or PythonInterpreter.get()
    self._inherit_path = pex_info.inherit_path
    self._supported_tags = []

    platform = Platform.current()
    platform_name = platform.platform
    super(PEXEnvironment, self).__init__(
      search_path=[] if pex_info.inherit_path == 'false' else sys.path,
      # NB: Our pkg_resources.Environment base-class wants the platform name string and not the
      # pex.platform.Platform object.
      platform=platform_name,
      **kw
    )
    self._target_interpreter_env = self._interpreter.identity.pkg_resources_env(platform_name)
    self._supported_tags.extend(platform.supported_tags(self._interpreter))
    TRACER.log(
      'E: tags for %r x %r -> %s' % (self.platform, self._interpreter, self._supported_tags),
      V=9
    )