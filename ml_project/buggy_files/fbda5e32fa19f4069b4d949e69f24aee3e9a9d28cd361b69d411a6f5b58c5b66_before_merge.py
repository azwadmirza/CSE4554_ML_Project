def create_key_from_series(namespace, fn, **kw):
    """Generate a key limiting the amount of dictionaries keys that are allowed to be used."""
    def generate_key(*arg, **kwargs):
        """
        Generate the key.

        The key is passed to the decorated function using the kwargs `storage_key`.
        Following this standard we can cache every object, using this key_generator.
        """
        try:
            if PY2:
                return kwargs['storage_key'].encode('utf-8')
            return kwargs['storage_key']
        except KeyError:
            log.exception('Make sure you pass kwargs parameter `storage_key` to configure the key,'
                          ' that is used in the dogpile cache.')

    return generate_key