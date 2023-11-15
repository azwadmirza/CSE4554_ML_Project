def wait_call(
    name,
    func,
    args=(),
    kws=None,
    stateful=False,
    use_vt=False,
    output_loglevel="debug",
    hide_output=False,
    **kwargs
):
    # Ignoring our arguments is intentional.
    return {"name": name, "changes": {}, "result": True, "comment": ""}