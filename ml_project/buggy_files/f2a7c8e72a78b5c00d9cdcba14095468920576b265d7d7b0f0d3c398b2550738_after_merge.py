def _minimize_cobyla(fun, x0, args=(), constraints=(),
                     rhobeg=1.0, tol=1e-4, maxiter=1000,
                     disp=False, catol=2e-4, **unknown_options):
    """
    Minimize a scalar function of one or more variables using the
    Constrained Optimization BY Linear Approximation (COBYLA) algorithm.

    Options
    -------
    rhobeg : float
        Reasonable initial changes to the variables.
    tol : float
        Final accuracy in the optimization (not precisely guaranteed).
        This is a lower bound on the size of the trust region.
    disp : bool
        Set to True to print convergence messages. If False,
        `verbosity` is ignored as set to 0.
    maxiter : int
        Maximum number of function evaluations.
    catol : float
        Tolerance (absolute) for constraint violations

    """
    _check_unknown_options(unknown_options)
    maxfun = maxiter
    rhoend = tol
    iprint = int(bool(disp))

    # check constraints
    if isinstance(constraints, dict):
        constraints = (constraints, )

    for ic, con in enumerate(constraints):
        # check type
        try:
            ctype = con['type'].lower()
        except KeyError:
            raise KeyError('Constraint %d has no type defined.' % ic)
        except TypeError:
            raise TypeError('Constraints must be defined using a '
                            'dictionary.')
        except AttributeError:
            raise TypeError("Constraint's type must be a string.")
        else:
            if ctype != 'ineq':
                raise ValueError("Constraints of type '%s' not handled by "
                                 "COBYLA." % con['type'])

        # check function
        if 'fun' not in con:
            raise KeyError('Constraint %d has no function defined.' % ic)

        # check extra arguments
        if 'args' not in con:
            con['args'] = ()

    # m is the total number of constraint values
    # it takes into account that some constraints may be vector-valued
    cons_lengths = []
    for c in constraints:
        f = c['fun'](x0, *c['args'])
        try:
            cons_length = len(f)
        except TypeError:
            cons_length = 1
        cons_lengths.append(cons_length)
    m = sum(cons_lengths)

    def calcfc(x, con):
        f = fun(x, *args)
        i = 0
        for size, c in izip(cons_lengths, constraints):
            con[i: i + size] = c['fun'](x, *c['args'])
            i += size
        return f

    info = np.zeros(4, np.float64)
    xopt, info = _cobyla.minimize(calcfc, m=m, x=np.copy(x0), rhobeg=rhobeg,
                                  rhoend=rhoend, iprint=iprint, maxfun=maxfun,
                                  dinfo=info)

    if info[3] > catol:
        # Check constraint violation
        info[0] = 4

    return OptimizeResult(x=xopt,
                          status=int(info[0]),
                          success=info[0] == 1,
                          message={1: 'Optimization terminated successfully.',
                                   2: 'Maximum number of function evaluations has '
                                      'been exceeded.',
                                   3: 'Rounding errors are becoming damaging in '
                                      'COBYLA subroutine.',
                                   4: 'Did not converge to a solution satisfying '
                                      'the constraints. See `maxcv` for magnitude '
                                      'of violation.'
                                   }.get(info[0], 'Unknown exit status.'),
                          nfev=int(info[1]),
                          fun=info[2],
                          maxcv=info[3])