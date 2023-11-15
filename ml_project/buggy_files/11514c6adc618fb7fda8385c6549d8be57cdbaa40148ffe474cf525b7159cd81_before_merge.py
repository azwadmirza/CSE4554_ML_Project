def _rhs_rho_milstein_implicit(L, rho_t, t, A, dt, ddW, d1, d2, args):
    """
    Drift implicit Milstein (theta = 1/2, eta = 0)
    Wang, X., Gan, S., & Wang, D. (2012). 
    A family of fully implicit Milstein methods for stiff stochastic differential 
    equations with multiplicative noise. 
    BIT Numerical Mathematics, 52(3), 741–772.
    """
    
    dW = ddW[:, 0]
    A = A[0]
    

    #reusable operators and traces
    a = A[-1] * rho_t * (0.5 * dt)
    e0 = cy_expect_rho_vec(A[0], rho_t, 1)
    b = A[0] * rho_t - e0 * rho_t
    TrAb = cy_expect_rho_vec(A[0], b, 1)

    drho_t = b * dW[0] 
    drho_t += a
    drho_t += (A[0] * b - TrAb * rho_t - e0 * b) * dW[1] # Milstein term
    drho_t += rho_t

    v, check = sp.linalg.bicgstab(A[-2], drho_t, x0 = drho_t + a, tol=args['tol'])

    return v