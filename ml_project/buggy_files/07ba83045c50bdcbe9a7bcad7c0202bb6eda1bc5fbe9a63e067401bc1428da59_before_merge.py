    def _is_valid(cls, *args, **kwargs):
        if 'header_spec' in kwargs:
            # Compute header size if header is customized
            header_spec = cls._setup_binary_spec(
                kwargs['header_spec'], gadget_header_specs)
            header_size = _compute_header_size(header_spec)
        else:
            header_size = 256
        # First 4 bytes used to check load
        return GadgetDataset._validate_header(args[0], header_size)[0]