def bitcast_convert_type(operand, new_dtype):
  new_dtype = xla_bridge.canonicalize_dtype(new_dtype)
  old_dtype = _dtype(operand)
  if old_dtype != new_dtype:
    return bitcast_convert_type_p.bind(operand, new_dtype=new_dtype)
  else:
    return operand