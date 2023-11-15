def odeint(ofunc, y0, t, *args, **kwargs):
  """Adaptive stepsize (Dormand-Prince) Runge-Kutta odeint implementation.

  Args:
    ofunc: Function to evaluate `yt = ofunc(y, t, *args)` that
      returns the time derivative of `y`.
    y0: initial value for the state.
    t: Timespan for `ofunc` evaluation like `np.linspace(0., 10., 101)`.
    *args: Additional arguments to `ofunc` beyond y0 and t.
    **kwargs: Two relevant keyword arguments:
      'rtol': Relative local error tolerance for solver.
      'atol': Absolute local error tolerance for solver.
      'mxstep': Maximum number of steps to take for each timepoint.

  Returns:
    Integrated system values at each timepoint.
  """
  rtol = kwargs.get('rtol', 1.4e-8)
  atol = kwargs.get('atol', 1.4e-8)
  mxstep = kwargs.get('mxstep', np.inf)

  func = lambda y, t: ofunc(y, t, *args)

  def _fori_body_fun(i, val):
    """Internal fori_loop body to interpolate an integral at each timestep."""
    t, cur_y, cur_f, cur_t, dt, last_t, interp_coeff, solution = val
    cur_y, cur_f, cur_t, dt, last_t, interp_coeff, _ = jax.lax.while_loop(
        lambda x: (x[2] < t[i]) & (x[-1] < mxstep),
        _while_body_fun,
        (cur_y, cur_f, cur_t, dt, last_t, interp_coeff, 0.))

    relative_output_time = (t[i] - last_t) / (cur_t - last_t)
    out_x = np.polyval(interp_coeff, relative_output_time)
    solution = jax.ops.index_update(solution, jax.ops.index[i, :], out_x)
    return (t, cur_y, cur_f, cur_t, dt, last_t, interp_coeff, solution)

  def _while_body_fun(x):
    """Internal while_loop body to determine interpolation coefficients."""
    cur_y, cur_f, cur_t, dt, last_t, interp_coeff, j = x
    next_t = cur_t + dt
    next_y, next_f, next_y_error, k = runge_kutta_step(func, cur_y, cur_f, cur_t, dt)
    error_ratios = error_ratio(next_y_error, rtol, atol, cur_y, next_y)
    new_interp_coeff = interp_fit_dopri(cur_y, next_y, k, dt)
    dt = optimal_step_size(dt, error_ratios)

    next_j = j + 1
    new = (next_y, next_f, next_t, dt, cur_t, new_interp_coeff, next_j)
    old = (cur_y, cur_f, cur_t, dt, last_t, interp_coeff, next_j)
    return tuple(map(partial(np.where, np.all(error_ratios <= 1.)), new, old))

  f0 = func(y0, t[0])
  dt = initial_step_size(func, t[0], y0, 4, rtol, atol, f0)
  interp_coeff = np.array([y0] * 5)
  solution = jax.ops.index_update(np.zeros((t.shape[0], y0.shape[0])),
                                  jax.ops.index[0, :], y0)
  init_carry = (t, y0, f0, t[0], dt, t[0], interp_coeff, solution)
  *_, solution = jax.lax.fori_loop(1, t.shape[0], _fori_body_fun, init_carry)
  return solution