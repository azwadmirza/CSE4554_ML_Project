def copy_func(f, workset_name):
    new_funcname = '{}_{}'.format(f.func_name, workset_name)
    new_func = \
        types.FunctionType(f.func_code,
                           f.func_globals,
                           new_funcname,
                           tuple([workset_name]),
                           f.func_closure)

    # set the docstring
    new_func.__doc__ = WORKSET_FUNC_DOCSTRING_TEMPLATE.format(workset_name)
    new_func.is_dependent = False
    return new_func