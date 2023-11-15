def _minimize_trustregion_exact(fun, x0, args=(), jac=None, hess=None,
                                **trust_region_options):
    """
    Minimization of scalar function of one or more variables using
    a nearly exact trust-region algorithm.

    Options
    -------
    initial_tr_radius : float
        Initial trust-region radius.
    max_tr_radius : float
        Maximum value of the trust-region radius. No steps that are longer
        than this value will be proposed.
    eta : float
        Trust region related acceptance stringency for proposed steps.
    gtol : float
        Gradient norm must be less than ``gtol`` before successful
        termination.
    """

    if jac is None:
        raise ValueError('Jacobian is required for trust region '
                         'exact minimization.')
    if hess is None:
        raise ValueError('Hessian matrix is required for trust region '
                         'exact minimization.')
    return _minimize_trust_region(fun, x0, args=args, jac=jac, hess=hess,
                                  subproblem=IterativeSubproblem,
                                  **trust_region_options)