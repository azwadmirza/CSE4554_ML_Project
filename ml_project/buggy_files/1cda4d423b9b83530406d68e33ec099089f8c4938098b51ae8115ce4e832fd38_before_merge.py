def compute_function_id(function):
    """Compute an function ID for a function.

    Args:
        func: The actual function.

    Returns:
        This returns the function ID.
    """
    function_id_hash = hashlib.sha1()
    # Include the function module and name in the hash.
    function_id_hash.update(function.__module__.encode("ascii"))
    function_id_hash.update(function.__name__.encode("ascii"))
    # If we are running a script or are in IPython, include the source code in
    # the hash. If we are in a regular Python interpreter we skip this part
    # because the source code is not accessible. If the function is a built-in
    # (e.g., Cython), the source code is not accessible.
    import __main__ as main
    if (hasattr(main, "__file__") or in_ipython()) \
            and inspect.isfunction(function):
        function_id_hash.update(inspect.getsource(function).encode("ascii"))
    # Compute the function ID.
    function_id = function_id_hash.digest()
    assert len(function_id) == 20
    function_id = ray.ObjectID(function_id)

    return function_id