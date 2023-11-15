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
    try:
        # If we are running a script or are in IPython, include the source code
        # in the hash.
        source = inspect.getsource(function).encode("ascii")
        function_id_hash.update(source)
    except (IOError, OSError, TypeError):
        # Source code may not be available: e.g. Cython or Python interpreter.
        pass
    # Compute the function ID.
    function_id = function_id_hash.digest()
    assert len(function_id) == 20
    function_id = ray.ObjectID(function_id)

    return function_id