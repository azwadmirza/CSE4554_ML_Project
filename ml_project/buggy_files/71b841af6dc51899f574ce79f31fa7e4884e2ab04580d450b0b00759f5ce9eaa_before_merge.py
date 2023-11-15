def xla_primitive_callable(prim, *arg_specs, **params):
  avals, devices = unzip2(arg_specs)
  # TODO(mattjj): make Device hashable instead of handling pairs here
  try:
    device, = set(d for d in devices if d is not None) or (None,)
  except ValueError:
    msg = "primitive arguments must be colocated on the same device, got {}"
    names = ("{}({})".format(d[0].__name__, d[1]) for d in devices if d is not None)
    raise ValueError(msg.format(", ".join(names)))
  else:
    all_devices = it.chain(xb.devices(), xb.devices('cpu'))
    device = device and next(d for d in all_devices if (type(d), d.id) == device)
  backend = xb.get_device_backend(device)
  aval_out = prim.abstract_eval(*avals, **params)
  if prim.multiple_results:
    handlers = tuple(map(aval_to_result_handler, aval_out))
    handle_result = lambda xs: tuple(h(x) for h, x in zip(handlers, xs.destructure()))
  else:
    handle_result = aval_to_result_handler(aval_out)
  tuple_args = len(avals) > 100
  built_c = primitive_computation(prim, backend, tuple_args, *avals, **params)
  options = xb.get_compile_options(device_assignment=(device.id,) if device else None)
  compiled = built_c.Compile(compile_options=options, backend=backend)
  return partial(_execute_compiled_primitive, prim, compiled, backend,
                 tuple_args, handle_result)