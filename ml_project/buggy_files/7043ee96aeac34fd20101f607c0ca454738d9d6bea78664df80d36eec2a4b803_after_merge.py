    def __setattr__(cls, name, value):
        # For symmetry with getattr and dir, pass all
        # attribute setting on to the module. (This makes
        # reloading work, see issue #805)
        setattr(_signal_module, name, value)