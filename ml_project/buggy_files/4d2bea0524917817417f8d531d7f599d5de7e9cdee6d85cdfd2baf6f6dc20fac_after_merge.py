def build_odeint(ofunc, rtol=1.4e-8, atol=1.4e-8, mxstep=np.inf):
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
  fwd = partial(odeint, ofunc, rtol=rtol, atol=atol, mxstep=mxstep)
  bwd = partial(vjp_odeint, ofunc, rtol=rtol, atol=atol, mxstep=mxstep)
  return custom_gradient(fwd, bwd)