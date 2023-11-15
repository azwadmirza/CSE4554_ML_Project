def _rhs_rho_taylor_15_implicit(L, rho_t, t, A, dt, ddW, d1, d2, args):
    """
    Drift implicit Taylor 1.5 (alpha = 1/2, beta = doesn't matter)
    Chaptert 12.2 Eq. (2.18) in Numerical Solution of Stochastic Differential Equations
    By Peter E. Kloeden, Eckhard Platen
    """
    
    dW = ddW[:, 0]
    A = A[0]

    #reusable operators and traces
    a = A[-1] * rho_t
    e0 = cy_expect_rho_vec(A[0], rho_t, 1)
    b = A[0] * rho_t - e0 * rho_t
    TrAb = cy_expect_rho_vec(A[0], b, 1)
    Lb = A[0] * b - TrAb * rho_t - e0 * b
    TrALb = cy_expect_rho_vec(A[0], Lb, 1)
    TrAa = cy_expect_rho_vec(A[0], a, 1)

    drho_t = b * dW[0] 
    drho_t += Lb * dW[1] # Milstein term
    xx0 = (drho_t + a * dt) + rho_t #starting vector for the linear solver (Milstein prediction)
    drho_t += (0.5 * dt) * a

    # new terms: 
    drho_t += A[-1] * b * (dW[2] - 0.5*dW[0]*dt)
    drho_t += (A[0] * a - TrAa * rho_t - e0 * a - TrAb * b) * dW[3]

    drho_t += (A[0] * Lb - TrALb * rho_t - (2 * TrAb) * b - e0 * Lb) * dW[4]
    drho_t += rho_t

    v, check = sp.linalg.bicgstab(A[-2], drho_t, x0 = xx0, tol=args['tol'])

    return v