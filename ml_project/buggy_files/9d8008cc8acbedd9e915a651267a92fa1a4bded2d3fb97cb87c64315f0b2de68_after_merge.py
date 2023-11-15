def model_json_decoder(dct):
    """
    Automatically deserialize Mopidy models from JSON.

    Usage::

        >>> import json
        >>> json.loads(
        ...     '{"a_track": {"__model__": "Track", "name": "name"}}',
        ...     object_hook=model_json_decoder)
        {u'a_track': Track(artists=[], name=u'name')}

    """
    # NOTE kwargs dict keys must be bytestrings to work on Python < 2.6.5
    # See https://github.com/mopidy/mopidy/issues/302 for details.
    if '__model__' in dct:
        model_name = dct.pop('__model__')
        cls = globals().get(model_name, None)
        if issubclass(cls, ImmutableObject):
            kwargs = {}
            for key, value in dct.items():
                kwargs[str(key)] = value
            return cls(**kwargs)
    return dct