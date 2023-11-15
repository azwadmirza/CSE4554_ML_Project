def _cpp_jit(
    fun: F,
    static_argnums: Union[int, Iterable[int]] = (),
    device: Optional[xc.Device] = None,
    backend: Optional[str] = None,
    donate_argnums: Union[int, Iterable[int]] = (),
) -> F:
  """An implementation of `jit` that tries to do as much as possible in C++.

  The goal of this function is to speed up the time it takes to process the
  arguments, find the correct C++ executable, start the transfer of arguments
  and schedule the computation.
  As long as it does not support all features of the Python implementation
  the C++ code will fallback to `_python_jit` when it faces some unsupported
  feature.
  """
  _check_callable(fun)
  static_argnums = _ensure_index_tuple(static_argnums)
  donate_argnums = _ensure_index_tuple(donate_argnums)
  donate_argnums = rebase_donate_argnums(donate_argnums, static_argnums)

  if device is not None and backend is not None:
    raise ValueError("can't specify both a device and a backend for jit, "
                     f"got device={device} and backend={backend}.")

  def cache_miss(_, *args, **kwargs):
    ### This first part is basically the same code as in _python_jit.
    # An alternative would be for cache_miss to accept from C++ the arguments
    # (dyn_args, donated_invars, args_flat, in_tree), since otherwise we have
    # work/code that is redundant between C++ and Python. We can try that later.
    if max(static_argnums + donate_argnums, default=-1) >= len(args):
      msg = ("jitted function has static_argnums={}, donate_argnums={} but "
             "was called with only {} positional arguments.")
      raise ValueError(msg.format(static_argnums, donate_argnums, len(args)))
    f = lu.wrap_init(fun)
    if static_argnums:
      f, dyn_args = argnums_partial_except(f, static_argnums, args)
    else:
      dyn_args = args
    args_flat, in_tree = tree_flatten((dyn_args, kwargs))
    if donate_argnums:
      donated_invars = donation_vector(donate_argnums, dyn_args, kwargs)
    else:
      donated_invars = (False,) * len(args_flat)

    for arg in args_flat:
      _check_arg(arg)
    flat_fun, out_tree = flatten_fun(f, in_tree)
    out_flat = xla.xla_call(
        flat_fun,
        *args_flat,
        device=device,
        backend=backend,
        name=flat_fun.__name__,
        donated_invars=donated_invars)
    out_pytree_def = out_tree()
    out = tree_unflatten(out_pytree_def, out_flat)

    ### Decide whether we can support the C++ fast path
    # High level note: The Python tracing mechanism is complex; in particular
    # to know whether `jax.jit(f)(x)` will execute or trace, it's not enough to
    # inspect the argument x, we actually do need to execute it and look at the
    # outputs that could be tracers (if f is capturing `Tracer` by closure).
    execute: Optional[functools.partial] = (
        xla._xla_callable.most_recent_entry())
    use_fastpath = (
        # This is if we have already executed this code-path (most-recent entry
        # has been reset to None). Thus, we do not support the fast-path.
        execute is not None and
        execute.func is xla._execute_compiled and  # not trivial, not pmap
        # Not supported: ShardedDeviceArray, DeviceConstant.
        all(xla.type_is_device_array(x) for x in out_flat) and
        # TODO(mattjj): Add support for lazy-expression.
        # If the input is a DeviceArray, then it should have a trivial LazyExpr.
        all(
            type(x) is not xla.DeviceArray or xla.lazy.is_trivial(x._lazy_expr)
            for x in args_flat))

    ### If we can use the fastpath, we return required info to the caller.
    if use_fastpath:
      xla_executable, _, result_handlers = execute.args
      sticky_device = None
      avals = []
      lazy_exprs = []
      for result_handler in result_handlers:
        aval, sticky_device, lazy_expr = result_handler.args
        avals.append(aval)
        lazy_exprs.append(None if xla.lazy.is_trivial(lazy_expr) else lazy_expr)
      assert len(avals) == len(out_flat)
      fastpath_data = (xla_executable, out_pytree_def, sticky_device, avals, lazy_exprs)
    else:
      fastpath_data = None

    return out, fastpath_data

  def get_device_info():
    """Backends do not exist before __main__ is being executed."""
    committed_to_device = device is not None or backend is not None

    if device is not None:
      default_device = device
    else:
      backend_ = xb.get_backend(backend)
      default_device = backend_.get_default_device_assignment(1)[0]

    return _BackendAndDeviceInfo(default_device, committed_to_device)

  def get_jax_enable_x64():
    """Returns the value of the flag after GoogleInit.

    We must wait until flags have been parsed (in particular for top-level
    functions decorated with jax.jit), so we delay inspecting the value
    of the jax_enable_x64 flag until JIT time.
    """
    # TODO(jblespiau): Delete when jaxlib 0.1.62 is the minimal version.
    if lib._xla_extension_version >= 4:
      return config.read("jax_enable_x64")
    else:
      return config.x64_enabled

  def get_jax_disable_jit_flag():
    """Returns the value of the `jax_disable_jit` flag.

    Both a flag and the `disable_jit` context manager can disable jit. We access
    the flag only once, when jitting the function, and the context manager
    modifies a C++ thread-local value.
    """
    return config.read("jax_disable_jit")

  static_argnums_ = (0,) + tuple(i + 1 for i in static_argnums)
  cpp_jitted_f = jax_jit.jit(fun, cache_miss, get_device_info,
                             get_jax_enable_x64, get_jax_disable_jit_flag,
                             static_argnums_)

  # TODO(mattjj): make cpp callable follow descriptor protocol for bound methods
  @wraps(fun)
  @api_boundary
  def f_jitted(*args, **kwargs):
    # TODO(jblespiau): We can remove `config.x64_enabled` when jaxlib has
    # extension version 4
    context = (getattr(core.thread_local_state.trace_state.trace_stack,
                         "dynamic", None), config.x64_enabled)
    # TODO(jblespiau): Move this to C++.
    if (FLAGS.jax_debug_nans or FLAGS.jax_debug_infs) and not _jit_is_disabled():
      device_arrays = cpp_jitted_f(context, *args, **kwargs)
      try:
        xla.check_special(xla.xla_call_p, [
            da.device_buffer
            for da in tree_leaves(device_arrays)
            if hasattr(da, "device_buffer")
        ])
        return device_arrays
      except FloatingPointError:
        assert FLAGS.jax_debug_nans or FLAGS.jax_debug_infs  # compiled_fun can only raise in this case
        print("Invalid nan value encountered in the output of a C++-jit "
              "function. Calling the de-optimized version.")
        return cache_miss(context, *args, **kwargs)[0]  # probably won't return
    elif _jit_is_disabled():
      return cpp_jitted_f(*args, **kwargs)
    else:
      return cpp_jitted_f(context, *args, **kwargs)
  f_jitted._cpp_jitted_f = cpp_jitted_f

  return f_jitted