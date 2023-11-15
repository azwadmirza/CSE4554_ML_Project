  def from_callable(cls, val):
    annotations = {argname(i): val.formal_type_parameters[i]
                   for i in range(val.num_args)}
    return cls(
        name="<callable>",
        param_names=tuple(sorted(annotations)),
        varargs_name=None,
        kwonly_params=set(),
        kwargs_name=None,
        defaults={},
        annotations=annotations,
    )