    def __new__(cls, file):
        # Remove trailing slashes.
        obj = str.__new__(cls, file)
        obj._is_function = isfunction(file) or ismethod(file)
        obj._is_function = obj._is_function or (
            isinstance(file, AnnotatedString) and bool(file.callable)
        )
        obj._file = file
        obj.rule = None
        obj._regex = None

        if obj.is_remote:
            obj.remote_object._iofile = obj

        obj.set_inventory_paths()
        return obj