    def _get_enabled(self, from_dict, default=None):
        '''
        Retrieve the enabled state from the given dict of host variables.

        The enabled variable may be specified as 'foo.bar', in which case
        the lookup will traverse into nested dicts, equivalent to:

        from_dict.get('foo', {}).get('bar', default)
        '''
        enabled = default
        if getattr(self, 'enabled_var', None):
            default = object()
            for key in self.enabled_var.split('.'):
                if not hasattr(from_dict, 'get'):
                    enabled = default
                    break
                enabled = from_dict.get(key, default)
                from_dict = enabled
            if enabled is not default:
                enabled_value = getattr(self, 'enabled_value', None)
                if enabled_value is not None:
                    enabled = bool(unicode(enabled_value) == unicode(enabled))
                else:
                    enabled = bool(enabled)
        if enabled is default:
            return None
        elif isinstance(enabled, bool):
            return enabled
        else:
            raise NotImplementedError('Value of enabled {} not understood.'.format(enabled))