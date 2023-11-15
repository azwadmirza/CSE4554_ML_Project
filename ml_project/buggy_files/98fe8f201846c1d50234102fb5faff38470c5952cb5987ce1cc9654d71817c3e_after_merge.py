def Find(name):
    f = None
    if name.startswith('__builtin__'):
        if name == '__builtin__.str':
            name = 'org.python.core.PyString'
        elif name == '__builtin__.dict':
            name = 'org.python.core.PyDictionary'

    mod = _imp(name)
    parent = mod
    foundAs = ''

    try:
        f = getattr(mod, '__file__', None)
    except:
        f = None


    components = name.split('.')
    old_comp = None
    for comp in components[1:]:
        try:
            #this happens in the following case:
            #we have mx.DateTime.mxDateTime.mxDateTime.pyd
            #but after importing it, mx.DateTime.mxDateTime does shadows access to mxDateTime.pyd
            mod = getattr(mod, comp)
        except AttributeError:
            if old_comp != comp:
                raise

        if hasattr(mod, '__file__'):
            f = mod.__file__
        else:
            if len(foundAs) > 0:
                foundAs = foundAs + '.'
            foundAs = foundAs + comp

        old_comp = comp
        
    if f is None and name.startswith('java.lang'):
        # Hack: java.lang.__file__ is None on Jython 2.7 (whereas it pointed to rt.jar on Jython 2.5).
        f = _java_rt_file

    if f is not None:
        if f.endswith('.pyc'):
            f = f[:-1]
        elif f.endswith('$py.class'):
            f = f[:-len('$py.class')] + '.py'
    return f, mod, parent, foundAs