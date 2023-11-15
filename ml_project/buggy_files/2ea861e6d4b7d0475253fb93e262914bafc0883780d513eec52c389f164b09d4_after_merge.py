    def is_applicable(cls, settings):
        syntax = settings.get('syntax')
        return is_supported_syntax(syntax) if syntax else False