    def __iter__(self):
        """Iterate through the top-level of the Dataset, yielding DataElements.

        >>> for elem in ds:
        >>>     print(elem)

        The DataElements are returned in increasing tag value order.
        Sequence items are returned as a single DataElement, so it is up to the
        calling code to recurse into the Sequence items if desired.

        Yields
        ------
        pydicom.dataelem.DataElement
            The Dataset's DataElements, sorted by increasing tag order.
        """
        # Note this is different than the underlying dict class,
        #        which returns the key of the key:value mapping.
        #   Here the value is returned (but data_element.tag has the key)
        taglist = sorted(self._dict.keys())
        for tag in taglist:
            yield self[tag]