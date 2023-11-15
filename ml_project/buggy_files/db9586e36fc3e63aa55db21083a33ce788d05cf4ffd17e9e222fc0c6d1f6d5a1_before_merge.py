    def __init__(self, parameter_name, parameter_value, source, wrong_type, valid_types, msg=None):
        self.wrong_type = wrong_type
        self.valid_types = valid_types
        if msg is None:
            msg = ("Parameter %s = %r declared in %s has type %s.\n"
                   "Valid types: %s." % (parameter_name, parameter_value,
                                         source, wrong_type, pretty_list(valid_types)))
        super(InvalidTypeError, self).__init__(parameter_name, parameter_value, source, msg=msg)