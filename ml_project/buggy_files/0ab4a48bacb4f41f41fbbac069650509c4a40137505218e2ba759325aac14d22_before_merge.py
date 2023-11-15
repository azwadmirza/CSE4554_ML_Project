def dogbox(fun, jac, x0, f0, J0, lb, ub, ftol, xtol, gtol, max_nfev, x_scale,
           loss_function, tr_solver, tr_options, verbose):
    f = f0
    f_true = f.copy()
    nfev = 1

    J = J0
    njev = 1

    if loss_function is not None:
        rho = loss_function(f)
        cost = 0.5 * np.sum(rho[0])
        J, f = scale_for_robust_loss_function(J, f, rho)
    else:
        cost = 0.5 * np.dot(f, f)

    g = compute_grad(J, f)

    jac_scale = isinstance(x_scale, str) and x_scale == 'jac'
    if jac_scale:
        scale, scale_inv = compute_jac_scale(J)
    else:
        scale, scale_inv = x_scale, 1 / x_scale

    Delta = norm(x0 * scale_inv, ord=np.inf)
    if Delta == 0:
        Delta = 1.0

    on_bound = np.zeros_like(x0, dtype=int)
    on_bound[np.equal(x0, lb)] = -1
    on_bound[np.equal(x0, ub)] = 1

    x = x0
    step = np.empty_like(x0)

    if max_nfev is None:
        max_nfev = x0.size * 100

    termination_status = None
    iteration = 0
    step_norm = None
    actual_reduction = None

    if verbose == 2:
        print_header_nonlinear()

    while True:
        active_set = on_bound * g < 0
        free_set = ~active_set

        g_free = g[free_set]
        g_full = g.copy()
        g[active_set] = 0

        g_norm = norm(g, ord=np.inf)
        if g_norm < gtol:
            termination_status = 1

        if verbose == 2:
            print_iteration_nonlinear(iteration, nfev, cost, actual_reduction,
                                      step_norm, g_norm)

        if termination_status is not None or nfev == max_nfev:
            break

        x_free = x[free_set]
        lb_free = lb[free_set]
        ub_free = ub[free_set]
        scale_free = scale[free_set]

        # Compute (Gauss-)Newton and build quadratic model for Cauchy step.
        if tr_solver == 'exact':
            J_free = J[:, free_set]
            newton_step = lstsq(J_free, -f, rcond=-1)[0]

            # Coefficients for the quadratic model along the anti-gradient.
            a, b = build_quadratic_1d(J_free, g_free, -g_free)
        elif tr_solver == 'lsmr':
            Jop = aslinearoperator(J)

            # We compute lsmr step in scaled variables and then
            # transform back to normal variables, if lsmr would give exact lsq
            # solution, this would be equivalent to not doing any
            # transformations, but from experience it's better this way.

            # We pass active_set to make computations as if we selected
            # the free subset of J columns, but without actually doing any
            # slicing, which is expensive for sparse matrices and impossible
            # for LinearOperator.

            lsmr_op = lsmr_operator(Jop, scale, active_set)
            newton_step = -lsmr(lsmr_op, f, **tr_options)[0][free_set]
            newton_step *= scale_free

            # Components of g for active variables were zeroed, so this call
            # is correct and equivalent to using J_free and g_free.
            a, b = build_quadratic_1d(Jop, g, -g)

        actual_reduction = -1.0
        while actual_reduction <= 0 and nfev < max_nfev:
            tr_bounds = Delta * scale_free

            step_free, on_bound_free, tr_hit = dogleg_step(
                x_free, newton_step, g_free, a, b, tr_bounds, lb_free, ub_free)

            step.fill(0.0)
            step[free_set] = step_free

            if tr_solver == 'exact':
                predicted_reduction = -evaluate_quadratic(J_free, g_free,
                                                          step_free)
            elif tr_solver == 'lsmr':
                predicted_reduction = -evaluate_quadratic(Jop, g, step)

            x_new = x + step
            f_new = fun(x_new)
            nfev += 1

            step_h_norm = norm(step * scale_inv, ord=np.inf)

            if not np.all(np.isfinite(f_new)):
                Delta = 0.25 * step_h_norm
                continue

            # Usual trust-region step quality estimation.
            if loss_function is not None:
                cost_new = loss_function(f_new, cost_only=True)
            else:
                cost_new = 0.5 * np.dot(f_new, f_new)
            actual_reduction = cost - cost_new

            Delta, ratio = update_tr_radius(
                Delta, actual_reduction, predicted_reduction,
                step_h_norm, tr_hit
            )

            step_norm = norm(step)
            termination_status = check_termination(
                actual_reduction, cost, step_norm, norm(x), ratio, ftol, xtol)

            if termination_status is not None:
                break

        if actual_reduction > 0:
            on_bound[free_set] = on_bound_free

            x = x_new
            # Set variables exactly at the boundary.
            mask = on_bound == -1
            x[mask] = lb[mask]
            mask = on_bound == 1
            x[mask] = ub[mask]

            f = f_new
            f_true = f.copy()

            cost = cost_new

            J = jac(x, f)
            njev += 1

            if loss_function is not None:
                rho = loss_function(f)
                J, f = scale_for_robust_loss_function(J, f, rho)

            g = compute_grad(J, f)

            if jac_scale:
                scale, scale_inv = compute_jac_scale(J, scale_inv)
        else:
            step_norm = 0
            actual_reduction = 0

        iteration += 1

    if termination_status is None:
        termination_status = 0

    return OptimizeResult(
        x=x, cost=cost, fun=f_true, jac=J, grad=g_full, optimality=g_norm,
        active_mask=on_bound, nfev=nfev, njev=njev, status=termination_status)