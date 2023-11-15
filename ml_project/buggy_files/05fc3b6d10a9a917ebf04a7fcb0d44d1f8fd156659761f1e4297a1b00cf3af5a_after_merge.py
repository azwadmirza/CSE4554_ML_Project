def _capture_function_code_using_source_copy(func) -> str:	
    func_code = inspect.getsource(func)

    #Function might be defined in some indented scope (e.g. in another function).
    #We need to handle this and properly dedent the function source code
    func_code = textwrap.dedent(func_code)
    func_code_lines = func_code.split('\n')

    # Removing possible decorators (can be multiline) until the function definition is found
    while func_code_lines and not func_code_lines[0].startswith('def '):
        del func_code_lines[0]

    if not func_code_lines:
        raise ValueError('Failed to dedent and clean up the source of function "{}". It is probably not properly indented.'.format(func.__name__))

    func_code = '\n'.join(func_code_lines)

    # Stripping type annotations to prevent import errors.
    # The most common cases are InputPath/OutputPath and typing.NamedTuple annotations
    func_code = strip_type_hints(func_code)

    return func_code