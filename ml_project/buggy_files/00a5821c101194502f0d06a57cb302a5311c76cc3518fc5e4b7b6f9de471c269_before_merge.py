    def _is_valid(self, *args, **kwargs):
        # First 4 bytes used to check load
        return GadgetDataset._validate_header(args[0])[0]