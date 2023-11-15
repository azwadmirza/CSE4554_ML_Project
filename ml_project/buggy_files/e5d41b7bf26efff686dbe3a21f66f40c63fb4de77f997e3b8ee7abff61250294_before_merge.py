def id_tap(tap_func, arg, *, result=None, tap_with_device=False, **kwargs):
  """Host-callback tap primitive, like identity function with a call to ``tap_func``.

  **Experimental: please give feedback, and expect changes!**

  ``id_tap`` behaves semantically like the identity function but has the
  side-effect that a user-defined Python function is called with the runtime
  value of the argument.

  Args:
    tap_func: tap function to call like ``tap_func(arg, transforms)``, with
      ``arg`` as described below and where ``transforms`` is the sequence of
      applied JAX transformations in the form ``(name, params)``. If the
      `tap_with_device` optional argument is True, then the invocation also
      includes the device from which the value is tapped as a keyword argument:
      ``tap_func(arg, transforms, device=dev)``.
    arg: the argument passed to the tap function, can be a pytree of JAX
      types.
    result: if given, specifies the return value of ``id_tap``. This value is
      not passed to the tap function, and in fact is not sent from the device to
      the host. If the ``result`` parameter is not specified then the return
      value of ``id_tap`` is ``arg``.
    tap_with_device: if True then the tap function is invoked with the
      device from which the tap originates as a keyword argument.

  Returns:
    ``arg``, or ``result`` if given.

  The order of execution is by data dependency: after all the arguments and
  the value of ``result`` if present, are computed and before the returned
  value is used. At least one of the returned values of ``id_tap`` must be
  used in the rest of the computation, or else this operation has no effect.

  Tapping works even for code executed on accelerators and even for code under
  JAX transformations.

  For more details see the
  `module documentation
  <jax.experimental.host_callback.html>`_.
  """
  if kwargs:
    msg = (
        "Support for **kwargs in ``id_tap`` has been removed. Instead, "
        "pre-apply keyword arguments, either by using a closure or by passing "
        "``functools.partial(tap_func, **kwargs)``.")
    raise TypeError(msg)

  if result is not None:
    flat_results, result_treedef = pytree.flatten(result)
    for result in flat_results:
      api._check_arg(result)

  call_res = _call(tap_func, arg, call_with_device=tap_with_device,
                   result_shape=None, identity=True)

  if result is not None:
    # Return the results, but add a dependency on the call, to ensure it
    # is kept in the graph.
    call_flat_results, _ = pytree.flatten(call_res)
    assert call_flat_results
    call_flat_results = [id_tap_dep_p.bind(r, call_flat_results[0])
                         for r in flat_results]
    return result_treedef.unflatten(call_flat_results)
  else:
    return call_res