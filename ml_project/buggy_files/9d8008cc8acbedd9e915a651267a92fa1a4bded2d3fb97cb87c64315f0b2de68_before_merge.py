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
    if '__model__' in dct:
        model_name = dct.pop('__model__')
        cls = globals().get(model_name, None)
        if issubclass(cls, ImmutableObject):
            return cls(**dct)
    return dct