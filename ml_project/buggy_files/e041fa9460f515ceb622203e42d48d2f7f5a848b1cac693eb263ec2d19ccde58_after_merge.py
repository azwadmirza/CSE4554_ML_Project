    def __new__(cls, *args, **kwargs):
        # resolves the parent instance
        instance = super().__new__(cls)
        if cls.get_contexts():
            potential_parent = cls.get_contexts()[-1]
            # We have to make sure that the context is a _DrawValuesContext
            # and not a Model
            if isinstance(potential_parent, _DrawValuesContext):
                instance._parent = potential_parent
            else:
                instance._parent = None
        else:
            instance._parent = None
        return instance