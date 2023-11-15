    def copy(self, **values):
        """
        Copy the model with ``field`` updated to new value.

        Examples::

            # Returns a track with a new name
            Track(name='foo').copy(name='bar')
            # Return an album with a new number of tracks
            Album(num_tracks=2).copy(num_tracks=5)

        :param values: the model fields to modify
        :type values: dict
        :rtype: new instance of the model being copied
        """
        # NOTE kwargs dict keys must be bytestrings to work on Python < 2.6.5
        # See https://github.com/mopidy/mopidy/issues/302 for details
        data = {}
        for key in self.__dict__.keys():
            public_key = key.lstrip('_')
            data[str(public_key)] = values.pop(public_key, self.__dict__[key])
        for key in values.keys():
            if hasattr(self, key):
                data[str(key)] = values.pop(key)
        if values:
            raise TypeError(
                'copy() got an unexpected keyword argument "%s"' % key)
        return self.__class__(**data)