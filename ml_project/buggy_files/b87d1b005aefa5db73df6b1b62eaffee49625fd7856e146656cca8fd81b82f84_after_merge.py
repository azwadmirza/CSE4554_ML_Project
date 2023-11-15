def _xla_callable(fun, device, backend, *arg_specs):
  if device is not None and backend is not None:
    raise ValueError("can't specify both a device and a backend for jit, "
                     "got device={} and backend={}".format(device, backend))

  abstract_args, arg_devices = unzip2(arg_specs)
  pvals = [pe.PartialVal((aval, core.unit)) for aval in abstract_args]
  with core.new_master(pe.StagingJaxprTrace, True) as master:
    jaxpr, (pvals, consts, env) = pe.trace_to_subjaxpr(fun, master, False).call_wrapped(pvals)
    assert not env  # no subtraces here
    del master, env
  _map(prefetch, it.chain(consts, jaxpr_literals(jaxpr)))

  nreps = jaxpr_replicas(jaxpr)
  device = _xla_callable_device(nreps, backend, device, arg_devices)
  result_handlers = tuple(map(partial(_pval_to_result_handler, device), pvals))

  # Computations that only produce constants and/or only rearrange their inputs,
  # which are often produced from partial evaluation, don't need compilation,
  # and don't need to force their (potentially lazy) arguments.
  if not jaxpr.eqns:
    device = device or xb.get_backend(None).get_default_device_assignment(1)[0]
    return partial(_execute_trivial, jaxpr, device, consts, result_handlers)

  log_priority = logging.WARNING if FLAGS.jax_log_compiles else logging.DEBUG
  logging.log(log_priority,
              "Compiling {} for args {}.".format(fun.__name__, abstract_args))

  if nreps > xb.device_count(backend):
    msg = ("compiling computation that requires {} replicas, but only {} XLA "
            "devices are available")
    raise ValueError(msg.format(nreps, xb.device_count(backend)))
  if xb.host_count() > 1 and (nreps > 1 or jaxpr_has_pmap(jaxpr)):
    raise NotImplementedError(
        "jit of multi-host pmap not implemented (and jit-of-pmap can cause "
        "extra data movement anyway, so maybe you don't want it after all).")

  tuple_args = len(abstract_args) > 100  # pass long arg lists as tuple for TPU

  c = xb.make_computation_builder("jit_{}".format(fun.__name__))
  xla_consts = _map(c.Constant, consts)
  xla_args = _xla_callable_args(c, abstract_args, tuple_args)
  out_nodes = jaxpr_subcomp(c, jaxpr, backend, AxisEnv(nreps, [], []),
                            xla_consts, (), *xla_args)
  built = c.Build(c.Tuple(*out_nodes))

  options = xb.get_compile_options(
      num_replicas=nreps, device_assignment=(device.id,) if device else None)
  compiled = built.Compile(compile_options=options, backend=xb.get_backend(backend))

  if nreps == 1:
    return partial(_execute_compiled, compiled, backend, result_handlers, tuple_args)
  else:
    return partial(_execute_replicated, compiled, backend, result_handlers, tuple_args)