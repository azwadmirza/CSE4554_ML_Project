  def cache_miss(_, *args, **kwargs):
    ### This first part is basically the same code as in _python_jit.
    # An alternative would be for cache_miss to accept from C++ the arguments
    # (dyn_args, donated_invars, args_flat, in_tree), since otherwise we have
    # work/code that is redundant between C++ and Python. We can try that later.
    if max(static_argnums + donate_argnums, default=-1) >= len(args):
      raise ValueError(f"jitted function has static_argnums={static_argnums}, "
                       f"donate_argnums={donate_argnums} but "
                       f"was called with only {len(args)} positional arguments.")
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
      if version >= (0, 1, 58):
        fastpath_data = (xla_executable, out_pytree_def, sticky_device, avals, lazy_exprs)
      else:
        fastpath_data = (xla_executable, result_handlers, out_pytree_def)
    else:
      fastpath_data = None

    return out, fastpath_data