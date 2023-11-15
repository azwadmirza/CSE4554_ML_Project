def yzy_to_zyz(xi, theta1, theta2, eps=1e-9):
    """Express a Y.Z.Y single qubit gate as a Z.Y.Z gate.

    Solve the equation

    .. math::

    Ry(2*theta1).Rz(2*xi).Ry(2*theta2) = Rz(2*phi).Ry(2*theta).Rz(2*lambda)

    for theta, phi, and lambda. This is equivalent to solving the system
    given in the comment for test_solution. Use eps for comparisons with zero.

    Return a solution theta, phi, and lambda.
    """
    solutions = []  # list of potential solutions
    # Four cases to avoid singularities
    # TODO investigate when these can be .is_zero
    if sympy.Abs(sympy.cos(xi)).evalf() < eps:
        solutions.append((theta2 - theta1, xi, 0))
    elif sympy.Abs(sympy.sin(theta1 + theta2)).evalf() < eps:
        phi_minus_lambda = [
            sympy.pi / 2,
            3 * sympy.pi / 2,
            sympy.pi / 2,
            3 * sympy.pi / 2]
        stheta_1 = sympy.asin(sympy.sin(xi) * sympy.sin(-theta1 + theta2))
        stheta_2 = sympy.asin(-sympy.sin(xi) * sympy.sin(-theta1 + theta2))
        stheta_3 = sympy.pi - stheta_1
        stheta_4 = sympy.pi - stheta_2
        stheta = [stheta_1, stheta_2, stheta_3, stheta_4]
        phi_plus_lambda = list(map(lambda x:
                                   sympy.acos(sympy.cos(theta1 + theta2) *
                                              sympy.cos(xi) / sympy.cos(x)),
                                   stheta))
        sphi = [(term[0] + term[1]) / 2 for term in
                zip(phi_plus_lambda, phi_minus_lambda)]
        slam = [(term[0] - term[1]) / 2 for term in
                zip(phi_plus_lambda, phi_minus_lambda)]
        solutions = list(zip(stheta, sphi, slam))
    elif sympy.Abs(sympy.cos(theta1 + theta2)).evalf() < eps:
        phi_plus_lambda = [
            sympy.pi / 2,
            3 * sympy.pi / 2,
            sympy.pi / 2,
            3 * sympy.pi / 2]
        stheta_1 = sympy.acos(sympy.sin(xi) * sympy.cos(theta1 - theta2))
        stheta_2 = sympy.acos(-sympy.sin(xi) * sympy.cos(theta1 - theta2))
        stheta_3 = -stheta_1
        stheta_4 = -stheta_2
        stheta = [stheta_1, stheta_2, stheta_3, stheta_4]
        phi_minus_lambda = list(map(lambda x:
                                    sympy.acos(sympy.sin(theta1 + theta2) *
                                               sympy.cos(xi) / sympy.sin(x)),
                                    stheta))
        sphi = [(term[0] + term[1]) / 2 for term in
                zip(phi_plus_lambda, phi_minus_lambda)]
        slam = [(term[0] - term[1]) / 2 for term in
                zip(phi_plus_lambda, phi_minus_lambda)]
        solutions = list(zip(stheta, sphi, slam))
    else:
        phi_plus_lambda = sympy.atan(sympy.sin(xi) * sympy.cos(theta1 - theta2) /
                                     (sympy.cos(xi) * sympy.cos(theta1 + theta2)))
        phi_minus_lambda = sympy.atan(sympy.sin(xi) * sympy.sin(-theta1 +
                                                                theta2) /
                                      (sympy.cos(xi) * sympy.sin(theta1 +
                                                                 theta2)))
        sphi = (phi_plus_lambda + phi_minus_lambda) / 2
        slam = (phi_plus_lambda - phi_minus_lambda) / 2
        solutions.append((sympy.acos(sympy.cos(xi) * sympy.cos(theta1 + theta2) /
                                     sympy.cos(sphi + slam)), sphi, slam))
        solutions.append((sympy.acos(sympy.cos(xi) * sympy.cos(theta1 + theta2) /
                                     sympy.cos(sphi + slam + sympy.pi)),
                          sphi + sympy.pi / 2,
                          slam + sympy.pi / 2))
        solutions.append((sympy.acos(sympy.cos(xi) * sympy.cos(theta1 + theta2) /
                                     sympy.cos(sphi + slam)),
                          sphi + sympy.pi / 2, slam - sympy.pi / 2))
        solutions.append((sympy.acos(sympy.cos(xi) * sympy.cos(theta1 + theta2) /
                                     sympy.cos(sphi + slam + sympy.pi)),
                          sphi + sympy.pi, slam))

    # Select the first solution with the required accuracy
    deltas = list(map(lambda x: test_trig_solution(x[0], x[1], x[2],
                                                   xi, theta1, theta2),
                      solutions))
    for delta_sol in zip(deltas, solutions):
        # TODO investigate when this can be .is_zero
        if delta_sol[0].evalf() < eps:
            return delta_sol[1]
    logger.debug("xi=%s", xi)
    logger.debug("theta1=%s", theta1)
    logger.debug("theta2=%s", theta2)
    logger.debug("solutions=%s", pprint.pformat(solutions))
    logger.debug("deltas=%s", pprint.pformat(deltas))
    assert False, "Error! No solution found. This should not happen."