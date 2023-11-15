def make_function_type(cfnptr):
    if cfnptr.argtypes is None:
        raise TypeError("ctypes function %r doesn't define its argument types; "
                        "consider setting the `argtypes` attribute"
                        % (cfnptr.__name__,))
    cargs = [convert_ctypes(a)
             for a in cfnptr.argtypes]
    cret = convert_ctypes(cfnptr.restype)
    if sys.platform == 'win32' and not cfnptr._flags_ & ctypes._FUNCFLAG_CDECL:
        # 'stdcall' calling convention under Windows
        cconv = 'x86_stdcallcc'
    else:
        # Default C calling convention
        cconv = None

    cases = [templates.signature(cret, *cargs)]
    template = templates.make_concrete_template("CFuncPtr", cfnptr, cases)

    pointer = ctypes.cast(cfnptr, ctypes.c_void_p).value
    return types.FunctionPointer(template, pointer, cconv=cconv)