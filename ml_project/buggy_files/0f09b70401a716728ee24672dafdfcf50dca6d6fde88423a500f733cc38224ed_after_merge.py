    def validate(self):
        super(Window, self).validate()

        window = self.window
        if isinstance(window, (list, tuple, np.ndarray)):
            pass
        elif com.is_integer(window):
            if window < 0:
                raise ValueError("window must be non-negative")
            try:
                import scipy.signal as sig
            except ImportError:
                raise ImportError('Please install scipy to generate window '
                                  'weight')

            if not isinstance(self.win_type, compat.string_types):
                raise ValueError('Invalid win_type {0}'.format(self.win_type))
            if getattr(sig, self.win_type, None) is None:
                raise ValueError('Invalid win_type {0}'.format(self.win_type))
        else:
            raise ValueError('Invalid window {0}'.format(window))