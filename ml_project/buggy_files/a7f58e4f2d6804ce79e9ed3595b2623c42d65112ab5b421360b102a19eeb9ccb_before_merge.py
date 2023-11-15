def is_field(var):
  if var is None or classgen.is_late_annotation(var):
    return False
  return isinstance(var.data[0], FieldInstance)