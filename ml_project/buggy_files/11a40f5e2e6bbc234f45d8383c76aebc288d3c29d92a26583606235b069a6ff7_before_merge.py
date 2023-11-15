  def _get_namedarg(self, args, name, default_value):
    if name not in args.namedargs:
      return default_value
    if name == "bound":
      return self._get_annotation(args.namedargs[name], name)
    else:
      ret = self._get_constant(args.namedargs[name], name, bool)
      # This error is logged only if _get_constant succeeds.
      self.vm.errorlog.not_supported_yet(
          self.vm.frames, "argument \"%s\" to TypeVar" % name)
      return ret