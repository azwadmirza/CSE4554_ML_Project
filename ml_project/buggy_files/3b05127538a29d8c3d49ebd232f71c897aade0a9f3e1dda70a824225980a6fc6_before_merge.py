    def _shallow_copy(self, values=None, **kwargs):
        """
        create a new Index with the same class as the caller, don't copy the
        data, use the same object attributes with passed in attributes taking
        precedence

        *this is an internal non-public method*

        Parameters
        ----------
        values : the values to create the new Index, optional
        kwargs : updates the default attributes for this Index
        """
        if values is None:
            values = self.values
        attributes = self._get_attributes_dict()
        attributes.update(kwargs)
        return self._simple_new(values, **attributes)