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