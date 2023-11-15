def xla_primitive_callable(prim, *arg_specs, **params):
  avals, arg_devices = unzip2(arg_specs)
  device = _device_from_arg_devices(arg_devices)
  backend = xb.get_device_backend(device)
  aval_out = prim.abstract_eval(*avals, **params)
  if not prim.multiple_results:
    handle_result = aval_to_result_handler(device, aval_out)
  else:
    handlers = tuple(map(partial(aval_to_result_handler, device), aval_out))
    handle_result = lambda xs: tuple(h(x) for h, x in zip(handlers, xs.destructure()))
  tuple_args = len(avals) > 100
  built_c = primitive_computation(prim, backend, tuple_args, *avals, **params)
  options = xb.get_compile_options(device_assignment=device and (device.id,))
  compiled = built_c.Compile(compile_options=options, backend=backend)
  return partial(_execute_compiled_primitive, prim, compiled, backend,
                 tuple_args, handle_result)