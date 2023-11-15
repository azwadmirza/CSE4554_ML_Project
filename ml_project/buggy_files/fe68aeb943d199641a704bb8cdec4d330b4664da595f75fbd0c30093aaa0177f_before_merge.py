    def deserialize(self, data):
        '''
        Given a dictionary of values, load up the field attributes for
        this object. As with serialize(), if there are any non-field
        attribute data members, this method will need to be overridden
        and extended.
        '''

        if not isinstance(data, dict):
            raise AnsibleAssertionError('data (%s) should be a dict but is a %s' % (data, type(data)))

        for (name, attribute) in iteritems(self._valid_attrs):
            if name in data:
                setattr(self, name, data[name])
            else:
                setattr(self, name, attribute.default)

        # restore the UUID field
        setattr(self, '_uuid', data.get('uuid'))
        self._finalized = data.get('finalized', False)
        self._squashed = data.get('squashed', False)