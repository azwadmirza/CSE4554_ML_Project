    def _is_valid(cls, *args, **kwargs):
        if 'header_spec' in kwargs:
            header_spec = kwargs['header_spec']
        else:
            header_spec = 'default'
        header = GadgetBinaryHeader(args[0], header_spec)
        return header.validate()