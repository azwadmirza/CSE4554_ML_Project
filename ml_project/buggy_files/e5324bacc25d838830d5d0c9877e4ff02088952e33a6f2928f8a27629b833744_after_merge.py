  def call(self, node, _, args):
    posargs = args.posargs
    if isinstance(args.namedargs, dict):
      namedargs = args.namedargs
    else:
      namedargs = self.vm.convert.value_to_constant(args.namedargs, dict)
    if namedargs and self.vm.python_version < (3, 6):
      errmsg = "Keyword syntax for NamedTuple is only supported in Python 3.6+"
      self.vm.errorlog.invalid_namedtuple_arg(self.vm.frames, err_msg=errmsg)
    if namedargs and len(posargs) == 1:
      namedargs = [abstract.Tuple(
          (self.vm.convert.build_string(node, k), v), self.vm).to_variable(node)
                   for k, v in namedargs.items()]
      namedargs = abstract.List(namedargs, self.vm).to_variable(node)
      posargs += (namedargs,)
      args = function.Args(posargs)
    elif namedargs:
      errmsg = ("Either list of fields or keywords can be provided to "
                "NamedTuple, not both")
      self.vm.errorlog.invalid_namedtuple_arg(self.vm.frames, err_msg=errmsg)
    return self.namedtuple.call(node, None, args)