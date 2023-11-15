def vjp_odeint(ofunc, y0, t, *args, **kwargs):
  """Return a function that calculates `vjp(odeint(func(y, t, *args))`.

  Args:
    ofunc: Function `ydot = ofunc(y, t, *args)` to compute the time
      derivative of `y`.
    y0: initial value for the state.
    t: Timespan for `ofunc` evaluation like `np.linspace(0., 10., 101)`.
    *args: Additional arguments to `ofunc` beyond y0 and t.
    **kwargs: Two relevant keyword arguments:
      'rtol': Relative local error tolerance for solver.
      'atol': Absolute local error tolerance for solver.
      'mxstep': Maximum number of steps to take for each timepoint.

  Returns:
    VJP function `vjp = vjp_all(g)` where `yt = ofunc(y, t, *args)`
    and g is used for VJP calculation. To evaluate the gradient w/ the VJP,
    supply `g = np.ones_like(yt)`. To evaluate the reverse Jacobian do a vmap
    over the standard basis of yt.
  """
  rtol = kwargs.get('rtol', 1.4e-8)
  atol = kwargs.get('atol', 1.4e-8)
  mxstep = kwargs.get('mxstep', np.inf)

  flat_args, unravel_args = ravel_pytree(args)
  flat_func = lambda y, t, flat_args: ofunc(y, t, *unravel_args(flat_args))

  @jax.jit
  def aug_dynamics(augmented_state, t, flat_args):
    """Original system augmented with vjp_y, vjp_t and vjp_args."""
    state_len = int(np.floor_divide(
        augmented_state.shape[0] - flat_args.shape[0] - 1, 2))
    y = augmented_state[:state_len]
    adjoint = augmented_state[state_len:2*state_len]
    dy_dt, vjpfun = jax.vjp(flat_func, y, t, flat_args)
    return np.hstack([np.ravel(dy_dt), np.hstack(vjpfun(-adjoint))])

  rev_aug_dynamics = lambda y, t, flat_args: -aug_dynamics(y, -t, flat_args)

  @jax.jit
  def _fori_body_fun(i, val):
    """fori_loop function for VJP calculation."""
    rev_yt, rev_t, rev_tarray, rev_gi, vjp_y, vjp_t0, vjp_args, time_vjp_list = val
    this_yt = rev_yt[i, :]
    this_t = rev_t[i]
    this_tarray = rev_tarray[i, :]
    this_gi = rev_gi[i, :]
    # this is g[i-1, :] when g has been reversed
    this_gim1 = rev_gi[i+1, :]
    state_len = this_yt.shape[0]
    vjp_cur_t = np.dot(flat_func(this_yt, this_t, flat_args), this_gi)
    vjp_t0 = vjp_t0 - vjp_cur_t
    # Run augmented system backwards to the previous observation.
    aug_y0 = np.hstack((this_yt, vjp_y, vjp_t0, vjp_args))
    aug_ans = odeint(rev_aug_dynamics, aug_y0, this_tarray, flat_args,
                     rtol=rtol, atol=atol, mxstep=mxstep)
    vjp_y = aug_ans[1][state_len:2*state_len] + this_gim1
    vjp_t0 = aug_ans[1][2*state_len]
    vjp_args = aug_ans[1][2*state_len+1:]
    time_vjp_list = jax.ops.index_update(time_vjp_list, i, vjp_cur_t)
    return rev_yt, rev_t, rev_tarray, rev_gi, vjp_y, vjp_t0, vjp_args, time_vjp_list

  @jax.jit
  def vjp_all(g, yt, t):
    """Calculate the VJP g * Jac(odeint(ofunc, y0, t, *args))."""
    rev_yt = yt[-1::-1, :]
    rev_t = t[-1::-1]
    rev_tarray = -np.array([t[-1:0:-1], t[-2::-1]]).T
    rev_gi = g[-1::-1, :]

    vjp_y = g[-1, :]
    vjp_t0 = 0.
    vjp_args = np.zeros_like(flat_args)
    time_vjp_list = np.zeros_like(t)

    init = (rev_yt, rev_t, rev_tarray, rev_gi, vjp_y, vjp_t0, vjp_args, time_vjp_list)
    result = jax.lax.fori_loop(0, rev_t.shape[0]-1, _fori_body_fun, init)

    time_vjp_list = jax.ops.index_update(result[-1], -1, result[-3])
    vjp_times = np.hstack(time_vjp_list)[::-1]

    return tuple([result[-4], vjp_times] + list(result[-2]))

  primals_out = odeint(flat_func, y0, t, flat_args, rtol=rtol, atol=atol, mxstep=mxstep)
  vjp_fun = lambda g: vjp_all(g, primals_out, t)

  return primals_out, vjp_fun