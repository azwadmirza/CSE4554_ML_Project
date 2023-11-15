def _instantiate_device_constant(const, device=None, backend=None, cutoff=1e6):
  # dispatch an XLA Computation to build the constant on the device if it's
  # large, or alternatively build it on the host and transfer it if it's small
  assert isinstance(const, DeviceConstant)
  backend = xb.get_backend(device.platform) if device else xb.get_backend(backend)
  if const.size > cutoff:
    c = xb.make_computation_builder("constant_instantiating_computation")
    xla_const = const.constant_handler(c, const)
    device_assignment = (device.id,) if device else None
    opts = xb.get_compile_options(device_assignment=device_assignment)
    compiled = c.Build(xla_const).Compile((), opts, backend=backend)
    return compiled.Execute(())
  else:
    return xc.Buffer.from_pyval(onp.asarray(const), device, backend=backend)