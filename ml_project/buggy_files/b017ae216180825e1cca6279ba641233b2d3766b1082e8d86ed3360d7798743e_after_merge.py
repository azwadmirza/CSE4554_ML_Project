    def __setitem__(self, key, value):
        """Operator for Dataset[key] = value.

        Check consistency, and deal with private tags.

        Parameters
        ----------
        key : int
            The tag for the element to be added to the Dataset.
        value : pydicom.dataelem.DataElement or pydicom.dataelem.RawDataElement
            The element to add to the Dataset.

        Raises
        ------
        NotImplementedError
            If `key` is a slice.
        ValueError
            If the `key` value doesn't match DataElement.tag.
        """
        if isinstance(key, slice):
            raise NotImplementedError('Slicing is not supported for setting '
                                      'Dataset elements.')

        # OK if is subclass, e.g. DeferredDataElement
        if not isinstance(value, (DataElement, RawDataElement)):
            raise TypeError("Dataset contents must be DataElement instances.")
        if isinstance(value.tag, BaseTag):
            tag = value.tag
        else:
            tag = Tag(value.tag)
        if key != tag:
            raise ValueError("DataElement.tag must match the dictionary key")

        data_element = value
        if tag.is_private:
            # See PS 3.5-2008 section 7.8.1 (p. 44) for how blocks are reserved
            logger.debug("Setting private tag %r" % tag)
            private_block = tag.elem >> 8
            private_creator_tag = Tag(tag.group, private_block)
            if private_creator_tag in self and tag != private_creator_tag:
                if data_element.is_raw:
                    data_element = DataElement_from_raw(
                        data_element, self._character_set)
                data_element.private_creator = self[private_creator_tag].value
        self._dict[tag] = data_element