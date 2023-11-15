    def clone(self, *args, **overrides):
        if len(args) == 1 and isinstance(args[0], tuple):
            args = args[0]
        # Apply name mangling for __ attribute
        pos_args = getattr(self, '_' + type(self).__name__ + '__pos_params', [])
        settings = {k: v for k, v in dict(self.get_param_values(), **overrides).items()
                    if k not in pos_args[:len(args)]}
        if 'id' not in settings:
            settings['id'] = self.id
        return self.__class__(*args, **settings)