    def should_store(self, value):
        return not (issubclass(value.dtype.type,
                               (np.integer, np.floating, np.complexfloating,
                                np.datetime64, np.bool_)) or
                    is_extension_type(value))