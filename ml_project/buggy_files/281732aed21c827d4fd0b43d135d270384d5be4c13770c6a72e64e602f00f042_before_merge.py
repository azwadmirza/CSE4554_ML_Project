    def elements(self):
        """Iterate through the top-level of the Dataset, yielding DataElements
        or RawDataElements (no conversion done).

        >>> for elem in ds.elements():
        >>>     print(elem)

        The elements are returned in the same way as in __getitem__.

        Yields
        ------
        pydicom.dataelem.DataElement or pydicom.dataelem.RawDataElement
            The Dataset's DataElements, sorted by increasing tag order.
        """
        taglist = sorted(self.tags.keys())
        for tag in taglist:
            yield self.get_item(tag)