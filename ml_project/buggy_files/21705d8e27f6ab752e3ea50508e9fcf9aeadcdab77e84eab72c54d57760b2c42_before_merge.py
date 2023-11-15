    def __init__(self, shape, default=None):
        """
        The basic shape class to be set in InputType.

        Attribute:

        shape: list of (int), symbolic values, RangeDim object
            The valid shape of the input
        default: tuple of int or None
            The default shape that is used for initiating the model, and set in
            the metadata of the model file.
            If None, then `shape` would be used.
        """
        from coremltools.converters.mil.mil import get_new_symbol

        if not isinstance(shape, (list, tuple)):
            msg = "Shape should be list or tuple, got type {} instead"
            raise ValueError(msg.format(type(shape)))
        self.symbolic_shape = []
        shape = list(shape)
        for idx, s in enumerate(shape):
            if s is None or s == -1:
                msg = 'Dimension cannot be None of -1. Use ' +\
                        'ct.RangeDim for runtime determined dimension. ' +\
                        'Dim {}: {} ' +\
                        'See https://coremltools.readme.io/docs/flexible-inputs'
                raise ValueError(msg.format(idx, s))
            if isinstance(s, RangeDim):
                sym = s.symbol
                self.symbolic_shape.append(sym)
            elif isinstance(s, (np.generic, six.integer_types)) or is_symbolic(s):
                self.symbolic_shape.append(s)
            else:
                raise ValueError(
                    "Unknown type {} to build symbolic shape.".format(type(s))
                )

        self.shape = tuple(shape)
        if default is not None:
            if not isinstance(default, (list, tuple)):
                raise ValueError(
                    "Default shape should be list or tuple, got type {} instead".format(
                        type(default)
                    )
                )
            for idx, s in enumerate(default):
                if not isinstance(
                    s, (np.generic, six.integer_types)
                ) and not is_symbolic(s):
                    raise ValueError(
                        "Default shape invalid, got error at index {} which is {}".format(
                            idx, s
                        )
                    )
        else:
            default = []
            for idx, s in enumerate(self.shape):
                if isinstance(s, RangeDim):
                    default.append(s.default)
                elif s is None or s == -1:
                    default.append(self.symbolic_shape[idx])
                else:
                    default.append(s)
        self.default = tuple(default)