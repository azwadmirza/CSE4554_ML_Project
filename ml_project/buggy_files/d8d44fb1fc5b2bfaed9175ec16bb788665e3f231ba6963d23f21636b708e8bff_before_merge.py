def aval_to_result_handler(aval):
  try:
    return xla_result_handlers[type(aval)](aval)
  except KeyError:
    raise TypeError("No xla_result_handler for type: {}".format(type(aval)))