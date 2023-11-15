    def __getattr__(self, name):
        """Intercept requests for Dataset attribute names.

        If `name` matches a DICOM keyword, return the value for the
        DataElement with the corresponding tag.

        Parameters
        ----------
        name
            A DataElement keyword or tag or a class attribute name.

        Returns
        -------
        value
              If `name` matches a DICOM keyword, returns the corresponding
              DataElement's value. Otherwise returns the class attribute's
              value (if present).
        """
        tag = tag_for_keyword(name)
        if tag is None:  # `name` isn't a DICOM element keyword
            # Try the base class attribute getter (fix for issue 332)
            return super(Dataset, self).__getattribute__(name)
        tag = Tag(tag)
        if tag not in self.tags:  # DICOM DataElement not in the Dataset
            # Try the base class attribute getter (fix for issue 332)
            return super(Dataset, self).__getattribute__(name)
        else:
            return self[tag].value