    def is_applicable(cls, settings):
        syntax = settings.get('syntax')
        if syntax is not None:
            return is_supported_syntax(syntax, client_configs.all)
        else:
            return False