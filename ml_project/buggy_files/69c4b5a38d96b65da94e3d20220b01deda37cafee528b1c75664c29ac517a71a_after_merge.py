def make_statements(code, variables, dtype, optimise=True, blockname=''):
    '''
    make_statements(code, variables, dtype, optimise=True, blockname='')

    Turn a series of abstract code statements into Statement objects, inferring
    whether each line is a set/declare operation, whether the variables are
    constant or not, and handling the cacheing of subexpressions.

    Parameters
    ----------
    code : str
        A (multi-line) string of statements.
    variables : dict-like
        A dictionary of with `Variable` and `Function` objects for every
        identifier used in the `code`.
    dtype : `dtype`
        The data type to use for temporary variables
    optimise : bool, optional
        Whether to optimise expressions, including
        pulling out loop invariant expressions and putting them in new
        scalar constants. Defaults to ``False``, since this function is also
        used just to in contexts where we are not interested by this kind of
        optimisation. For the main code generation stage, its value is set by
        the `codegen.loop_invariant_optimisations` preference.
    blockname : str, optional
        A name for the block (used to name intermediate variables to avoid
        name clashes when multiple blocks are used together)
    Returns
    -------
    scalar_statements, vector_statements : (list of `Statement`, list of `Statement`)
        Lists with statements that are to be executed once and statements that
        are to be executed once for every neuron/synapse/... (or in a vectorised
        way)

    Notes
    -----
    If ``optimise`` is ``True``, then the
    ``scalar_statements`` may include newly introduced scalar constants that
    have been identified as loop-invariant and have therefore been pulled out
    of the vector statements. The resulting statements will also use augmented
    assignments where possible, i.e. a statement such as ``w = w + 1`` will be
    replaced by ``w += 1``. Also, statements involving booleans will have
    additional information added to them (see `Statement` for details)
    describing how the statement can be reformulated as a sequence of if/then
    statements. Calls `~brian2.codegen.optimisation.optimise_statements`.
    '''
    code = strip_empty_lines(deindent(code))
    lines = re.split(r'[;\n]', code)
    lines = [LineInfo(code=line) for line in lines if len(line)]
    # Do a copy so we can add stuff without altering the original dict
    variables = dict(variables)
    # we will do inference to work out which lines are := and which are =
    defined = set(k for k, v in variables.items()
                  if not isinstance(v, AuxiliaryVariable))
    for line in lines:
        statement = None
        # parse statement into "var op expr"
        var, op, expr, comment = parse_statement(line.code)
        if var in variables and isinstance(variables[var], Subexpression):
            raise SyntaxError("Illegal line '{line}' in abstract code. "
                              "Cannot write to subexpression "
                              "'{var}'.".format(line=line.code,
                                                var=var))
        if op == '=':
            if var not in defined:
                op = ':='
                defined.add(var)
                if var not in variables:
                    annotated_ast = brian_ast(expr, variables)
                    is_scalar = annotated_ast.scalar
                    if annotated_ast.dtype == 'boolean':
                        use_dtype = bool
                    elif annotated_ast.dtype == 'integer':
                        use_dtype = int
                    else:
                        use_dtype = dtype
                    new_var = AuxiliaryVariable(var, dtype=use_dtype,
                                                scalar=is_scalar)
                    variables[var] = new_var
            elif not variables[var].is_boolean:
                sympy_expr = str_to_sympy(expr, variables)
                if variables[var].is_integer:
                    sympy_var = sympy.Symbol(var, integer=True)
                else:
                    sympy_var = sympy.Symbol(var, real=True)
                try:
                    collected = sympy.collect(sympy_expr, sympy_var,
                                              exact=True, evaluate=False)
                except AttributeError:
                    # If something goes wrong during collection, e.g. collect
                    # does not work for logical expressions
                    collected = {1: sympy_expr}

                if (len(collected) == 2 and
                        set(collected.keys()) == {1, sympy_var} and
                        collected[sympy_var] == 1):
                    # We can replace this statement by a += assignment
                    statement = Statement(var, '+=',
                                          sympy_to_str(collected[1]),
                                          comment,
                                          dtype=variables[var].dtype,
                                          scalar=variables[var].scalar)
                elif len(collected) == 1 and sympy_var in collected:
                    # We can replace this statement by a *= assignment
                    statement = Statement(var, '*=',
                                          sympy_to_str(collected[sympy_var]),
                                          comment,
                                          dtype=variables[var].dtype,
                                          scalar=variables[var].scalar)
        if statement is None:
            statement = Statement(var, op, expr, comment,
                                  dtype=variables[var].dtype,
                                  scalar=variables[var].scalar)

        line.statement = statement
        # for each line will give the variable being written to
        line.write = var 
        # each line will give a set of variables which are read
        line.read = get_identifiers_recursively([expr], variables)

    # All writes to scalar variables must happen before writes to vector
    # variables
    scalar_write_done = False
    for line in lines:
        stmt = line.statement
        if stmt.op != ':=' and variables[stmt.var].scalar and scalar_write_done:
            raise SyntaxError(('All writes to scalar variables in a code block '
                               'have to be made before writes to vector '
                               'variables. Illegal write to %s.') % line.write)
        elif not variables[stmt.var].scalar:
            scalar_write_done = True

    # all variables which are written to at some point in the code block
    # used to determine whether they should be const or not
    all_write = set(line.write for line in lines)

    # backwards compute whether or not variables will be read again
    # note that will_read for a line gives the set of variables it will read
    # on the current line or subsequent ones. will_write gives the set of
    # variables that will be written after the current line
    will_read = set()
    will_write = set()
    for line in lines[::-1]:
        will_read = will_read.union(line.read)
        line.will_read = will_read.copy()
        line.will_write = will_write.copy()
        will_write.add(line.write)

    subexpressions = dict((name, val) for name, val in variables.items()
                          if isinstance(val, Subexpression))
    # Check that no scalar subexpression refers to a vectorised function
    # (e.g. rand()) -- otherwise it would be differently interpreted depending
    # on whether it is used in a scalar or a vector context (i.e., even though
    # the subexpression is supposed to be scalar, it would be vectorised when
    # used as part of non-scalar expressions)
    for name, subexpr in subexpressions.items():
        if subexpr.scalar:
            identifiers = get_identifiers(subexpr.expr)
            for identifier in identifiers:
                if (identifier in variables and
                        getattr(variables[identifier],
                                'auto_vectorise', False)):
                    raise SyntaxError(('The scalar subexpression {} refers to '
                                       'the implicitly vectorised function {} '
                                       '-- this is not allowed since it leads '
                                       'to different interpretations of this '
                                       'subexpression depending on whether it '
                                       'is used in a scalar or vector '
                                       'context.').format(name, identifier))

    # sort subexpressions into an order so that subexpressions that don't depend
    # on other subexpressions are first
    subexpr_deps = dict((name, [dep for dep in subexpr.identifiers
                                if dep in subexpressions])
                        for name, subexpr in subexpressions.items())
    sorted_subexpr_vars = topsort(subexpr_deps)

    statements = []

    # none are yet defined (or declared)
    subdefined = dict((name, None) for name in subexpressions)
    for line in lines:
        stmt = line.statement
        read = line.read
        write = line.write
        will_read = line.will_read
        will_write = line.will_write
        # update/define all subexpressions needed by this statement
        for var in sorted_subexpr_vars:
            if var not in read:
                continue

            subexpression = subexpressions[var]
            # if already defined/declared
            if subdefined[var] == 'constant':
                continue
            elif subdefined[var] == 'variable':
                op = '='
                constant = False
            else:
                op = ':='
                # check if the referred variables ever change
                ids = subexpression.identifiers
                constant = all(v not in will_write for v in ids)
                subdefined[var] = 'constant' if constant else 'variable'

            statement = Statement(var, op, subexpression.expr, comment='',
                                  dtype=variables[var].dtype,
                                  constant=constant,
                                  subexpression=True,
                                  scalar=variables[var].scalar)
            statements.append(statement)

        var, op, expr, comment = stmt.var, stmt.op, stmt.expr, stmt.comment

        # constant only if we are declaring a new variable and we will not
        # write to it again
        constant = op == ':=' and var not in will_write
        statement = Statement(var, op, expr, comment,
                              dtype=variables[var].dtype,
                              constant=constant,
                              scalar=variables[var].scalar)
        statements.append(statement)

    scalar_statements = [s for s in statements if s.scalar]
    vector_statements = [s for s in statements if not s.scalar]

    if optimise and prefs.codegen.loop_invariant_optimisations:
        scalar_statements, vector_statements = optimise_statements(scalar_statements,
                                                                   vector_statements,
                                                                   variables,
                                                                   blockname=blockname)

    return scalar_statements, vector_statements