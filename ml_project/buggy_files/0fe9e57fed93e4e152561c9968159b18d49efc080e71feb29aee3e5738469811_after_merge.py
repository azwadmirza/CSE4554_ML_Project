def yzy_to_zyz(xi, theta1, theta2, eps=1e-9):
    """Express a Y.Z.Y single qubit gate as a Z.Y.Z gate.

    Solve the equation

    .. math::

    Ry(theta1).Rz(xi).Ry(theta2) = Rz(phi).Ry(theta).Rz(lambda)

    for theta, phi, and lambda.

    Return a solution theta, phi, and lambda.
    """
    Q = quaternion_from_euler([theta1, xi, theta2], 'yzy')
    euler = Q.to_zyz()
    P = quaternion_from_euler(euler, 'zyz')
    # output order different than rotation order
    out_angles = (euler[1], euler[0], euler[2])
    abs_inner = abs(P.data.dot(Q.data))
    if not np.allclose(abs_inner, 1, eps):
        logger.debug("xi=%s", xi)
        logger.debug("theta1=%s", theta1)
        logger.debug("theta2=%s", theta2)
        logger.debug("solutions=%s", out_angles)
        logger.debug("abs_inner=%s", abs_inner)
        raise MapperError('YZY and ZYZ angles do not give same rotation matrix.')
    return out_angles