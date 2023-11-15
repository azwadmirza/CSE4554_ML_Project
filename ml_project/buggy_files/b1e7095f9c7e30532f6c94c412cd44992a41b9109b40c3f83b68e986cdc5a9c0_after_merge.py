def _get_argspecs(glyphclass):
    argspecs = OrderedDict()
    for arg in glyphclass._args:
        spec = {}
        prop = getattr(glyphclass, arg)

        # running python with -OO will discard docstrings -> __doc__ is None
        if prop.__doc__:
            spec['desc'] = " ".join(x.strip() for x in prop.__doc__.strip().split("\n\n")[0].split('\n'))
        else:
            spec['desc'] = ""
        spec['default'] = prop.class_default(glyphclass)
        spec['type'] = prop.__class__.__name__
        argspecs[arg] = spec
    return argspecs