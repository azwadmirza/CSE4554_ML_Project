def show_options(solver=None, method=None, disp=True):
    """
    Show documentation for additional options of optimization solvers.

    These are method-specific options that can be supplied through the
    ``options`` dict.

    Parameters
    ----------
    solver : str
        Type of optimization solver. One of 'minimize', 'minimize_scalar',
        'root', or 'linprog'.
    method : str, optional
        If not given, shows all methods of the specified solver. Otherwise,
        show only the options for the specified method. Valid values
        corresponds to methods' names of respective solver (e.g., 'BFGS' for
        'minimize').
    disp : bool, optional
        Whether to print the result rather than returning it.

    Returns
    -------
    text
        Either None (for disp=True) or the text string (disp=False)

    Notes
    -----
    The solver-specific methods are:

    `scipy.optimize.minimize`

    - :ref:`Nelder-Mead <optimize.minimize-neldermead>`
    - :ref:`Powell      <optimize.minimize-powell>`
    - :ref:`CG          <optimize.minimize-cg>`
    - :ref:`BFGS        <optimize.minimize-bfgs>`
    - :ref:`Newton-CG   <optimize.minimize-newtoncg>`
    - :ref:`L-BFGS-B    <optimize.minimize-lbfgsb>`
    - :ref:`TNC         <optimize.minimize-tnc>`
    - :ref:`COBYLA      <optimize.minimize-cobyla>`
    - :ref:`SLSQP       <optimize.minimize-slsqp>`
    - :ref:`dogleg      <optimize.minimize-dogleg>`
    - :ref:`trust-ncg   <optimize.minimize-trustncg>`

    `scipy.optimize.root`

    - :ref:`hybr              <optimize.root-hybr>`
    - :ref:`lm                <optimize.root-lm>`
    - :ref:`broyden1          <optimize.root-broyden1>`
    - :ref:`broyden2          <optimize.root-broyden2>`
    - :ref:`anderson          <optimize.root-anderson>`
    - :ref:`linearmixing      <optimize.root-linearmixing>`
    - :ref:`diagbroyden       <optimize.root-diagbroyden>`
    - :ref:`excitingmixing    <optimize.root-excitingmixing>`
    - :ref:`krylov            <optimize.root-krylov>`
    - :ref:`df-sane           <optimize.root-dfsane>`

    `scipy.optimize.minimize_scalar`

    - :ref:`brent       <optimize.minimize_scalar-brent>`
    - :ref:`golden      <optimize.minimize_scalar-golden>`
    - :ref:`bounded     <optimize.minimize_scalar-bounded>`

    `scipy.optimize.linprog`

    - :ref:`simplex           <optimize.linprog-simplex>`
    - :ref:`interior-point    <optimize.linprog-interior-point>`
    - :ref:`revised simplex   <optimize.linprog-revised_simplex>`
    - :ref:`highs             <optimize.linprog-highs>`
    - :ref:`highs-ds          <optimize.linprog-highs-ds>`
    - :ref:`highs-ipm         <optimize.linprog-highs-ipm>`

    `scipy.optimize.quadratic_assignment`

    - :ref:`faq             <optimize.qap-faq>`
    - :ref:`2opt            <optimize.qap-2opt>`

    Examples
    --------
    We can print documentations of a solver in stdout:

    >>> from scipy.optimize import show_options
    >>> show_options(solver="minimize")
    ...

    Specifying a method is possible:

    >>> show_options(solver="minimize", method="Nelder-Mead")
    ...

    We can also get the documentations as a string:

    >>> show_options(solver="minimize", method="Nelder-Mead", disp=False)
    Minimization of scalar function of one or more variables using the ...

    """
    import textwrap

    doc_routines = {
        'minimize': (
            ('bfgs', 'scipy.optimize.optimize._minimize_bfgs'),
            ('cg', 'scipy.optimize.optimize._minimize_cg'),
            ('cobyla', 'scipy.optimize.cobyla._minimize_cobyla'),
            ('dogleg', 'scipy.optimize._trustregion_dogleg._minimize_dogleg'),
            ('l-bfgs-b', 'scipy.optimize.lbfgsb._minimize_lbfgsb'),
            ('nelder-mead', 'scipy.optimize.optimize._minimize_neldermead'),
            ('newton-cg', 'scipy.optimize.optimize._minimize_newtoncg'),
            ('powell', 'scipy.optimize.optimize._minimize_powell'),
            ('slsqp', 'scipy.optimize.slsqp._minimize_slsqp'),
            ('tnc', 'scipy.optimize.tnc._minimize_tnc'),
            ('trust-ncg', 'scipy.optimize._trustregion_ncg._minimize_trust_ncg'),
        ),
        'root': (
            ('hybr', 'scipy.optimize.minpack._root_hybr'),
            ('lm', 'scipy.optimize._root._root_leastsq'),
            ('broyden1', 'scipy.optimize._root._root_broyden1_doc'),
            ('broyden2', 'scipy.optimize._root._root_broyden2_doc'),
            ('anderson', 'scipy.optimize._root._root_anderson_doc'),
            ('diagbroyden', 'scipy.optimize._root._root_diagbroyden_doc'),
            ('excitingmixing', 'scipy.optimize._root._root_excitingmixing_doc'),
            ('linearmixing', 'scipy.optimize._root._root_linearmixing_doc'),
            ('krylov', 'scipy.optimize._root._root_krylov_doc'),
            ('df-sane', 'scipy.optimize._spectral._root_df_sane'),
        ),
        'root_scalar': (
            ('bisect', 'scipy.optimize._root_scalar._root_scalar_bisect_doc'),
            ('brentq', 'scipy.optimize._root_scalar._root_scalar_brentq_doc'),
            ('brenth', 'scipy.optimize._root_scalar._root_scalar_brenth_doc'),
            ('ridder', 'scipy.optimize._root_scalar._root_scalar_ridder_doc'),
            ('toms748', 'scipy.optimize._root_scalar._root_scalar_toms748_doc'),
            ('secant', 'scipy.optimize._root_scalar._root_scalar_secant_doc'),
            ('newton', 'scipy.optimize._root_scalar._root_scalar_newton_doc'),
            ('halley', 'scipy.optimize._root_scalar._root_scalar_halley_doc'),
        ),
        'linprog': (
            ('simplex', 'scipy.optimize._linprog._linprog_simplex_doc'),
            ('interior-point', 'scipy.optimize._linprog._linprog_ip_doc'),
            ('revised simplex', 'scipy.optimize._linprog._linprog_rs_doc'),
            ('highs-ipm', 'scipy.optimize._linprog._linprog_highs_ipm_doc'),
            ('highs-ds', 'scipy.optimize._linprog._linprog_highs_ds_doc'),
            ('highs', 'scipy.optimize._linprog._linprog_highs_doc'),
        ),
        'quadratic_assignment': (
            ('faq', 'scipy.optimize._qap._quadratic_assignment_faq'),
            ('2opt', 'scipy.optimize._qap._quadratic_assignment_2opt'),
        ),
        'minimize_scalar': (
            ('brent', 'scipy.optimize.optimize._minimize_scalar_brent'),
            ('bounded', 'scipy.optimize.optimize._minimize_scalar_bounded'),
            ('golden', 'scipy.optimize.optimize._minimize_scalar_golden'),
        ),
    }

    if solver is None:
        text = ["\n\n\n========\n", "minimize\n", "========\n"]
        text.append(show_options('minimize', disp=False))
        text.extend(["\n\n===============\n", "minimize_scalar\n",
                     "===============\n"])
        text.append(show_options('minimize_scalar', disp=False))
        text.extend(["\n\n\n====\n", "root\n",
                     "====\n"])
        text.append(show_options('root', disp=False))
        text.extend(['\n\n\n=======\n', 'linprog\n',
                     '=======\n'])
        text.append(show_options('linprog', disp=False))
        text = "".join(text)
    else:
        solver = solver.lower()
        if solver not in doc_routines:
            raise ValueError('Unknown solver %r' % (solver,))

        if method is None:
            text = []
            for name, _ in doc_routines[solver]:
                text.extend(["\n\n" + name, "\n" + "="*len(name) + "\n\n"])
                text.append(show_options(solver, name, disp=False))
            text = "".join(text)
        else:
            method = method.lower()
            methods = dict(doc_routines[solver])
            if method not in methods:
                raise ValueError("Unknown method %r" % (method,))
            name = methods[method]

            # Import function object
            parts = name.split('.')
            mod_name = ".".join(parts[:-1])
            __import__(mod_name)
            obj = getattr(sys.modules[mod_name], parts[-1])

            # Get doc
            doc = obj.__doc__
            if doc is not None:
                text = textwrap.dedent(doc).strip()
            else:
                text = ""

    if disp:
        print(text)
        return
    else:
        return text