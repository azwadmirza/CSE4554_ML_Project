  def _process_annotation(param):
    """Process a single param into either annotations or late_annotations."""
    if not param.typ:
      return
    elif isinstance(param.typ, cfg.Variable):
      if all(t.cls for t in param.typ.data):
        types = param.typ.data
        if len(types) == 1:
          annotations[param.name] = types[0].cls
        else:
          t = abstract.Union([t.cls for t in types], vm)
          annotations[param.name] = t
    elif isinstance(param.typ, abstract.LateAnnotation):
      late_annotations[param.name] = param.typ
    else:
      annotations[param.name] = param.typ