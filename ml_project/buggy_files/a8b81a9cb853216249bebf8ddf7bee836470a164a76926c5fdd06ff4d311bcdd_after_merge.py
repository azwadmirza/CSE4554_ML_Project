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