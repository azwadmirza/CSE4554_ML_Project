def make_function_type(cfnptr):
    cargs = [convert_ctypes(a)
             for a in cfnptr.argtypes]
    cret = convert_ctypes(cfnptr.restype)

    cases = [templates.signature(cret, *cargs)]
    template = templates.make_concrete_template("CFuncPtr", cfnptr, cases)

    pointer = ctypes.cast(cfnptr, ctypes.c_void_p).value
    return types.FunctionPointer(template, pointer)