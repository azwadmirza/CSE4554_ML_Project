  def _while_body_fun(func, x):
    """Internal while_loop body to determine interpolation coefficients."""
    cur_y, cur_f, cur_t, dt, last_t, interp_coeff, j = x
    next_t = cur_t + dt
    next_y, next_f, next_y_error, k = runge_kutta_step(
        func, cur_y, cur_f, cur_t, dt)
    error_ratios = error_ratio(next_y_error, rtol, atol, cur_y, next_y)
    new_interp_coeff = interp_fit_dopri(cur_y, next_y, k, dt)
    dt = optimal_step_size(dt, error_ratios)

    next_j = j + 1
    new_rav, unravel = ravel_pytree(
        (next_y, next_f, next_t, dt, cur_t, new_interp_coeff, next_j))
    old_rav, _ = ravel_pytree(
        (cur_y, cur_f, cur_t, dt, last_t, interp_coeff, next_j))

    return unravel(np.where(np.all(error_ratios <= 1.),
                            new_rav,
                            old_rav))