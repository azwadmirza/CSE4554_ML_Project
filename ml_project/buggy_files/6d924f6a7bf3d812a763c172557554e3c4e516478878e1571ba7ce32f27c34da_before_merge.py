  def from_pytd(cls, vm, name, sig):
    """Construct an abstract signature from a pytd signature."""
    # TODO(kramm): templates
    pytd_annotations = [(p.name, p.type)
                        for p in sig.params + (sig.starargs, sig.starstarargs)
                        if p is not None]
    pytd_annotations.append(("return", sig.return_type))
    def param_to_var(p):
      return vm.convert.constant_to_var(
          p.type, subst=datatypes.AliasingDict(), node=vm.root_cfg_node)
    return cls(
        name=name,
        param_names=tuple(p.name for p in sig.params if not p.kwonly),
        varargs_name=None if sig.starargs is None else sig.starargs.name,
        kwonly_params=set(p.name for p in sig.params if p.kwonly),
        kwargs_name=None if sig.starstarargs is None else sig.starstarargs.name,
        defaults={p.name: param_to_var(p) for p in sig.params if p.optional},
        annotations={name: vm.convert.constant_to_value(
            typ, subst=datatypes.AliasingDict(), node=vm.root_cfg_node)
                     for name, typ in pytd_annotations},
        late_annotations={},
        postprocess_annotations=False,
    )