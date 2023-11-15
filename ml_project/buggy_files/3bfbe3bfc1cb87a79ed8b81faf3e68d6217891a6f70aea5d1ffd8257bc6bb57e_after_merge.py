    def expand_options(cls, options, backend=None):
        """
        Validates and expands a dictionaries of options indexed by
        type[.group][.label] keys into separate style, plot and norm
        options.

            opts.expand_options({'Image': dict(cmap='viridis', show_title=False)})

        returns

            {'Image': {'plot': dict(show_title=False), 'style': dict(cmap='viridis')}}
        """
        current_backend = Store.current_backend
        backend_options = Store.options(backend=backend or current_backend)
        expanded = {}
        for objspec, options in options.items():
            objtype = objspec.split('.')[0]
            if objtype not in backend_options:
                raise ValueError('%s type not found, could not apply options.'
                                 % objtype)
            obj_options = backend_options[objtype]
            expanded[objspec] = {g: {} for g in obj_options.groups}
            for opt, value in options.items():
                found = False
                valid_options = []
                for g, group_opts in sorted(obj_options.groups.items()):
                    if opt in group_opts.allowed_keywords:
                        expanded[objspec][g][opt] = value
                        found = True
                        break
                    valid_options += group_opts.allowed_keywords
                if found: continue
                cls._options_error(opt, objtype, backend, valid_options)
        return expanded