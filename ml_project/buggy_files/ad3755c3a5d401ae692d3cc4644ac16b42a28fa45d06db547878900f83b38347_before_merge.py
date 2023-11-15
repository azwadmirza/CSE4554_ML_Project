def protfunc_parser(value, available_functions=None, testing=False, stacktrace=False, **kwargs):
    """
    Parse a prototype value string for a protfunc and process it.

    Available protfuncs are specified as callables in one of the modules of
    `settings.PROTFUNC_MODULES`, or specified on the command line.

    Args:
        value (any): The value to test for a parseable protfunc. Only strings will be parsed for
            protfuncs, all other types are returned as-is.
        available_functions (dict, optional): Mapping of name:protfunction to use for this parsing.
            If not set, use default sources.
        testing (bool, optional): Passed to protfunc. If in a testing mode, some protfuncs may
            behave differently.
        stacktrace (bool, optional): If set, print the stack parsing process of the protfunc-parser.

    Kwargs:
        session (Session): Passed to protfunc. Session of the entity spawning the prototype.
        protototype (dict): Passed to protfunc. The dict this protfunc is a part of.
        current_key(str): Passed to protfunc. The key in the prototype that will hold this value.
        any (any): Passed on to the protfunc.

    Returns:
        testresult (tuple): If `testing` is set, returns a tuple (error, result) where error is
            either None or a string detailing the error from protfunc_parser or seen when trying to
            run `literal_eval` on the parsed string.
        any (any): A structure to replace the string on the prototype level. If this is a
            callable or a (callable, (args,)) structure, it will be executed as if one had supplied
            it to the prototype directly. This structure is also passed through literal_eval so one
            can get actual Python primitives out of it (not just strings). It will also identify
            eventual object #dbrefs in the output from the protfunc.

    """
    if not isinstance(value, basestring):
        try:
            value = value.dbref
        except AttributeError:
            pass
        value = to_str(value, force_string=True)

    available_functions = PROT_FUNCS if available_functions is None else available_functions

    # insert $obj(#dbref) for #dbref
    value = _RE_DBREF.sub("$obj(\\1)", value)

    result = inlinefuncs.parse_inlinefunc(
        value, available_funcs=available_functions,
        stacktrace=stacktrace, testing=testing, **kwargs)

    err = None
    try:
        result = literal_eval(result)
    except ValueError:
        pass
    except Exception as err:
        err = str(err)
    if testing:
        return err, result
    return result