def _lower_array_expr(lowerer, expr):
    '''Lower an array expression built by RewriteArrayExprs.
    '''
    expr_name = "__numba_array_expr_%s" % (hex(hash(expr)).replace("-", "_"))
    expr_filename = expr.loc.filename
    expr_var_list = expr.list_vars()
    # The expression may use a given variable several times, but we
    # should only create one parameter for it.
    expr_var_unique = sorted(set(expr_var_list), key=lambda var: var.name)

    # Arguments are the names external to the new closure
    expr_args = [var.name for var in expr_var_unique]

    # 1. Create an AST tree from the array expression.
    with _legalize_parameter_names(expr_var_unique) as expr_params:
        ast_args = [ast.arg(param_name, None)
                    for param_name in expr_params]
        # Parse a stub function to ensure the AST is populated with
        # reasonable defaults for the Python version.
        ast_module = ast.parse('def {0}(): return'.format(expr_name),
                               expr_filename, 'exec')
        assert hasattr(ast_module, 'body') and len(ast_module.body) == 1
        ast_fn = ast_module.body[0]
        ast_fn.args.args = ast_args
        ast_fn.body[0].value, namespace = _arr_expr_to_ast(expr.expr)
        ast.fix_missing_locations(ast_module)

    # 2. Compile the AST module and extract the Python function.
    code_obj = compile(ast_module, expr_filename, 'exec')
    exec(code_obj, namespace)
    impl = namespace[expr_name]

    # 3. Now compile a ufunc using the Python function as kernel.

    context = lowerer.context
    builder = lowerer.builder
    outer_sig = expr.ty(*(lowerer.typeof(name) for name in expr_args))
    inner_sig_args = []
    for argty in outer_sig.args:
        if isinstance(argty, types.Optional):
            argty = argty.type
        if isinstance(argty, types.Array):
            inner_sig_args.append(argty.dtype)
        else:
            inner_sig_args.append(argty)
    inner_sig = outer_sig.return_type.dtype(*inner_sig_args)

    # Follow the Numpy error model.  Note this also allows e.g. vectorizing
    # division (issue #1223).
    flags = compiler.Flags()
    flags.set('error_model', 'numpy')
    cres = context.compile_subroutine(builder, impl, inner_sig, flags=flags,
                                      caching=False)

    # Create kernel subclass calling our native function
    from numba.np import npyimpl

    class ExprKernel(npyimpl._Kernel):
        def generate(self, *args):
            arg_zip = zip(args, self.outer_sig.args, inner_sig.args)
            cast_args = [self.cast(val, inty, outty)
                         for val, inty, outty in arg_zip]
            result = self.context.call_internal(
                builder, cres.fndesc, inner_sig, cast_args)
            return self.cast(result, inner_sig.return_type,
                             self.outer_sig.return_type)

    args = [lowerer.loadvar(name) for name in expr_args]
    return npyimpl.numpy_ufunc_kernel(
        context, builder, outer_sig, args, ExprKernel, explicit_output=False)