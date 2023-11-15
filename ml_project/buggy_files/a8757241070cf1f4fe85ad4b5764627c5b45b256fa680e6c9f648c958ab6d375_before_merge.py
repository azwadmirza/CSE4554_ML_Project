  def from_param_names(cls, name, param_names):
    """Construct a minimal signature from a name and a list of param names."""
    return cls(
        name=name,
        param_names=tuple(param_names),
        varargs_name=None,
        kwonly_params=set(),
        kwargs_name=None,
        defaults={},
        annotations={},
        late_annotations={}
    )