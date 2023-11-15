    def setdefault(self, key, default=None):
        """Emulate dictionary `setdefault`, but additionally support
        tag ID tuple and DICOM keyword for `key`, and data element value
        for `default`.

        .. usage:

        >>> ds = Dataset()
        >>> pname = ds.setdefault((0x0010, 0x0010), "Test")
        >>> pname
        (0010, 0010) Patient's Name                      PN: 'Test'
        >>> pname.value
        'Test'
        >>> psex = ds.setdefault('PatientSex',
        ...     DataElement(0x00100040, 'CS', 'F'))
        >>> psex.value
        'F'

        Parameters
        ----------
        key: int or str or 2-tuple
            if tuple - the group and element number of the DICOM tag
            if int - the combined group/element number
            if str - the DICOM keyword of the tag

        default: DataElement or value type or None
            The default value that is inserted and returned if no data
            element exists for the given key.
            If it is not of type DataElement, a DataElement is constructed
            instead for the given tag ID and default as value. This is only
            possible for known tags (e.g. tags found via the dictionary
            lookup).

        Returns
        -------
        The data element for `key` if it exists, or the default value if
        it is a DataElement or None, or a DataElement constructed with
        `default` as value.

        Raises
        ------
        KeyError
            If the key is not a valid tag ID or keyword.
            If no tag exists for `key`, default is not a DataElement
            and not None, and key is not a known DICOM tag.
        """
        if key in self:
            return self[key]
        if default is not None:
            if not isinstance(default, DataElement):
                tag = Tag(key)
                vr = datadict.dictionary_VR(tag)
                default = DataElement(Tag(key), vr, default)
            self[key] = default
        return default