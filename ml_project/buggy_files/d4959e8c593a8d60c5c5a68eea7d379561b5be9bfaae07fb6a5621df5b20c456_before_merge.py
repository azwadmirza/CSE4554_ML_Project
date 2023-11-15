    def writes(self, nb, **kwargs):
        kwargs['cls'] = BytesEncoder
        kwargs['indent'] = 1
        kwargs['sort_keys'] = True
        kwargs['separators'] = (',',': ')
        if kwargs.pop('split_lines', True):
            nb = split_lines(copy.deepcopy(nb))
        return json.dumps(nb, **kwargs)