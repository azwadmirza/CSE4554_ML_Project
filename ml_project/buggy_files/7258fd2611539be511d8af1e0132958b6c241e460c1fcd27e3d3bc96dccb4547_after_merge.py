    def _setup_binary_spec(cls, spec, spec_dict):
        if isinstance(spec, string_types):
            _hs = ()
            for hs in spec.split("+"):
                _hs += spec_dict[hs]
            spec = _hs
        return spec