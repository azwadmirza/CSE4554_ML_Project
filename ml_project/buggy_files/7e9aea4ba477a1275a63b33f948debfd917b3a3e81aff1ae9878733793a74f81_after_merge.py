    def deserialize(self, cstruct=colander.null):
        """Preprocess received data to carefully merge defaults.
        """
        if cstruct is not colander.null:
            defaults = cstruct.get('defaults')
            requests = cstruct.get('requests')
            if isinstance(defaults, dict) and isinstance(requests, list):
                for request in requests:
                    if isinstance(request, dict):
                        merge_dicts(request, defaults)
        return super(BatchPayloadSchema, self).deserialize(cstruct)