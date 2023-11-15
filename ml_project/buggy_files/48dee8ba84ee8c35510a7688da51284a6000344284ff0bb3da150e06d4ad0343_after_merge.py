def send_super(receiver, selName, *args, superclass_name=None, **kwargs):
    if hasattr(receiver, '_as_parameter_'):
        receiver = receiver._as_parameter_
    if superclass_name is None:
        superclass = get_superclass_of_object(receiver)
    else:
        superclass = get_class(superclass_name)
    super_struct = OBJC_SUPER(receiver, superclass)
    selector = get_selector(selName)
    restype = kwargs.get('restype', c_void_p)
    argtypes = kwargs.get('argtypes', None)
    objc.objc_msgSendSuper.restype = restype
    if argtypes:
        objc.objc_msgSendSuper.argtypes = [OBJC_SUPER_PTR, c_void_p] + argtypes
    else:
        objc.objc_msgSendSuper.argtypes = None
    result = objc.objc_msgSendSuper(byref(super_struct), selector, *args)
    if restype == c_void_p:
        result = c_void_p(result)
    return result