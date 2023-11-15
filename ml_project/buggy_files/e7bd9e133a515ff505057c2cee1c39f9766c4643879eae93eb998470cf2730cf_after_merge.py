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
            if isinstance(comp_dists, Distribution):
                comp_mode_logps = comp_dists.logp(comp_dists.mode)
            else:
                comp_mode_logps = tt.stack([cd.logp(cd.mode) for cd in comp_dists])

            mode_idx = tt.argmax(tt.log(w) + comp_mode_logps, axis=-1)
            self.mode = self._comp_modes()[mode_idx]

            if 'mode' not in defaults:
                defaults.append('mode')
        except (AttributeError, ValueError, IndexError):
            pass

        super().__init__(shape, dtype, defaults=defaults, *args, **kwargs)