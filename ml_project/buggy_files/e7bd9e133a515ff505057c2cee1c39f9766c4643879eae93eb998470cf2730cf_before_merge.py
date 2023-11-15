    def __init__(self, w, comp_dists, *args, **kwargs):
        # comp_dists type checking
        if not (
            isinstance(comp_dists, Distribution)
            or (
                isinstance(comp_dists, Iterable)
                and all((isinstance(c, Distribution) for c in comp_dists))
            )
        ):
            raise TypeError(
                "Supplied Mixture comp_dists must be a "
                "Distribution or an iterable of "
                "Distributions. Got {} instead.".format(
                    type(comp_dists)
                    if not isinstance(comp_dists, Iterable)
                    else [type(c) for c in comp_dists]
                )
            )
        shape = kwargs.pop('shape', ())

        self.w = w = tt.as_tensor_variable(w)
        self.comp_dists = comp_dists

        defaults = kwargs.pop('defaults', [])

        if all_discrete(comp_dists):
            default_dtype = _conversion_map[theano.config.floatX]
        else:
            default_dtype = theano.config.floatX

            try:
                self.mean = (w * self._comp_means()).sum(axis=-1)

                if 'mean' not in defaults:
                    defaults.append('mean')
            except AttributeError:
                pass
        dtype = kwargs.pop('dtype', default_dtype)

        try:
            comp_modes = self._comp_modes()
            comp_mode_logps = self.logp(comp_modes)
            self.mode = comp_modes[tt.argmax(w * comp_mode_logps, axis=-1)]

            if 'mode' not in defaults:
                defaults.append('mode')
        except (AttributeError, ValueError, IndexError):
            pass

        super().__init__(shape, dtype, defaults=defaults, *args, **kwargs)