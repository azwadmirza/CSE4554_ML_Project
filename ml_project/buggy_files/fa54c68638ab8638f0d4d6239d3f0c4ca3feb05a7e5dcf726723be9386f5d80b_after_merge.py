    def from_value(value):
        if value is None:
            return Channel(name="<unknown>")
        if hasattr(value, 'decode'):
            value = value.decode(UTF8)
        if has_scheme(value):
            if value.startswith('file:') and on_win:
                value = value.replace('\\', '/')
            return Channel.from_url(value)
        elif value.startswith(('./', '..', '~', '/')) or is_windows_path(value):
            return Channel.from_url(path_to_url(value))
        elif value.endswith('.tar.bz2'):
            if value.startswith('file:') and on_win:
                value = value.replace('\\', '/')
            return Channel.from_url(value)
        else:
            # at this point assume we don't have a bare (non-scheme) url
            #   e.g. this would be bad:  repo.continuum.io/pkgs/free
            if value in context.custom_multichannels:
                return MultiChannel(value, context.custom_multichannels[value])
            else:
                return Channel.from_channel_name(value)