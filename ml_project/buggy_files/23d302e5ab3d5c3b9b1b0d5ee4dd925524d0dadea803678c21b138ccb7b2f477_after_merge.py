def infer_sig_from_docstring(docstr: Optional[str], name: str) -> Optional[List[FunctionSig]]:
    """Convert function signature to list of TypedFunctionSig

    Look for function signatures of function in docstring. Signature is a string of
    the format <function_name>(<signature>) -> <return type> or perhaps without
    the return type.

    Returns empty list, when no signature is found, one signature in typical case,
    multiple signatures, if docstring specifies multiple signatures for overload functions.
    Return None if the docstring is empty.

    Arguments:
        * docstr: docstring
        * name: name of function for which signatures are to be found
    """
    if not docstr:
        return None

    state = DocStringParser(name)
    # Return all found signatures, even if there is a parse error after some are found.
    with contextlib.suppress(tokenize.TokenError):
        try:
            tokens = tokenize.tokenize(io.BytesIO(docstr.encode('utf-8')).readline)
            for token in tokens:
                state.add_token(token)
        except IndentationError:
            return None
    sigs = state.get_signatures()

    def is_unique_args(sig: FunctionSig) -> bool:
        """return true if function argument names are unique"""
        return len(sig.args) == len(set((arg.name for arg in sig.args)))

    # Return only signatures that have unique argument names. Mypy fails on non-uniqnue arg names.
    return [sig for sig in sigs if is_unique_args(sig)]