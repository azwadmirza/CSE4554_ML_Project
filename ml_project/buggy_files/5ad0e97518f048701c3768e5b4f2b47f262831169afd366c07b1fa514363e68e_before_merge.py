def call(
    name,
    func,
    args=(),
    kws=None,
    onlyif=None,
    unless=None,
    creates=None,
    output_loglevel="debug",
    hide_output=False,
    use_vt=False,
    **kwargs
):
    """
    Invoke a pre-defined Python function with arguments specified in the state
    declaration. This function is mainly used by the
    :mod:`salt.renderers.pydsl` renderer.

    The interpretation of ``onlyif`` and ``unless`` arguments are identical to
    those of :mod:`cmd.run <salt.states.cmd.run>`, and all other
    arguments(``cwd``, ``runas``, ...) allowed by :mod:`cmd.run
    <salt.states.cmd.run>` are allowed here, except that their effects apply
    only to the commands specified in `onlyif` and `unless` rather than to the
    function to be invoked.

    In addition, the ``stateful`` argument has no effects here.

    The return value of the invoked function will be interpreted as follows.

    If it's a dictionary then it will be passed through to the state system,
    which expects it to have the usual structure returned by any salt state
    function.

    Otherwise, the return value (denoted as ``result`` in the code below) is
    expected to be a JSON serializable object, and this dictionary is returned:

    .. code-block:: python

        {
            'name': name
            'changes': {'retval': result},
            'result': True if result is None else bool(result),
            'comment': result if isinstance(result, six.string_types) else ''
        }
    """
    ret = {"name": name, "changes": {}, "result": False, "comment": ""}

    cmd_kwargs = {
        "cwd": kwargs.get("cwd"),
        "runas": kwargs.get("user"),
        "shell": kwargs.get("shell") or __grains__["shell"],
        "env": kwargs.get("env"),
        "use_vt": use_vt,
        "output_loglevel": output_loglevel,
        "hide_output": hide_output,
        "umask": kwargs.get("umask"),
    }

    cret = mod_run_check(cmd_kwargs, onlyif, unless, creates)
    if isinstance(cret, dict):
        ret.update(cret)
        return ret

    if not kws:
        kws = {}
    result = func(*args, **kws)
    if isinstance(result, dict):
        ret.update(result)
        return ret
    else:
        # result must be JSON serializable else we get an error
        ret["changes"] = {"retval": result}
        ret["result"] = True if result is None else bool(result)
        if isinstance(result, six.string_types):
            ret["comment"] = result
        return ret