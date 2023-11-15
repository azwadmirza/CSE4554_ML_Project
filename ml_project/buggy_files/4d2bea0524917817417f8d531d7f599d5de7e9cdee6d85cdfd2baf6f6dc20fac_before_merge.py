def build_odeint(ofunc, rtol=1.4e-8, atol=1.4e-8, mxstep=onp.inf):
  """Return `f(y0, t, args) = odeint(ofunc(y, t, *args), y0, t, args)`.

  Given the function ofunc(y, t, *args), return the jitted function
  `f(y0, t, args) = odeint(ofunc(y, t, *args), y0, t, args)` with
  the VJP of `f` defined using `vjp_odeint`, where:

    `y0` is the initial condition of the ODE integration,
    `t` is the time course of the integration, and
    `*args` are all other arguments to `ofunc`.

  Args:
    ofunc: The function to be wrapped into an ODE integration.
    rtol: relative local error tolerance for solver.
    atol: absolute local error tolerance for solver.
    mxstep: Maximum number of steps to take for each timepoint.

  Returns:
    `f(y0, t, args) = odeint(ofunc(y, t, *args), y0, t, args)`
  """
  ct_odeint = jax.custom_transforms(
      lambda y0, t, *args: odeint(ofunc, y0, t, *args, rtol=rtol, atol=atol, mxstep=mxstep))

  v = lambda y0, t, *args: vjp_odeint(ofunc, y0, t, *args, rtol=rtol, atol=atol, mxstep=mxstep)
  jax.defvjp_all(ct_odeint, v)

  return jax.jit(ct_odeint)