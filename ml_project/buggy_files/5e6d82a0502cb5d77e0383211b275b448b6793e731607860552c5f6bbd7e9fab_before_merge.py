  def _fori_body_fun(func, i, val):
    """Internal fori_loop body to interpolate an integral at each timestep."""
    t, cur_y, cur_f, cur_t, dt, last_t, interp_coeff, solution = val
    cur_y, cur_f, cur_t, dt, last_t, interp_coeff, _ = jax.lax.while_loop(
        lambda x: (x[2] < t[i]) & (x[-1] < mxstep),
        functools.partial(_while_body_fun, func),
        (cur_y, cur_f, cur_t, dt, last_t, interp_coeff, 0.))

    relative_output_time = (t[i] - last_t) / (cur_t - last_t)
    out_x = np.polyval(interp_coeff, relative_output_time)

    return (t, cur_y, cur_f, cur_t, dt, last_t, interp_coeff,
            jax.ops.index_update(solution,
                                 jax.ops.index[i, :],
                                 out_x))