    def __getitem__(self, key):
        """Operator for Dataset[key] request.

        Any deferred data elements will be read in and an attempt will be made
        to correct any elements with ambiguous VRs.

        Examples
        --------
        Indexing using DataElement tag
        >>> ds = Dataset()
        >>> ds.SOPInstanceUID = '1.2.3'
        >>> ds.PatientName = 'CITIZEN^Jan'
        >>> ds.PatientID = '12345'
        >>> ds[0x00100010]
        'CITIZEN^Jan'

        Slicing using DataElement tag
        All group 0x0010 elements in the dataset
        >>> ds[0x00100000:0x0011000]
        (0010, 0010) Patient's Name                      PN: 'CITIZEN^Jan'
        (0010, 0020) Patient ID                          LO: '12345'

        All group 0x0002 elements in the dataset
        >>> ds[(0x0002, 0x0000):(0x0003, 0x0000)]

        Parameters
        ----------
        key
            The DICOM (group, element) tag in any form accepted by
            pydicom.tag.Tag such as [0x0010, 0x0010], (0x10, 0x10), 0x00100010,
            etc. May also be a slice made up of DICOM tags.

        Returns
        -------
        pydicom.dataelem.DataElement or pydicom.dataset.Dataset
            If a single DICOM element tag is used then returns the
            corresponding DataElement. If a slice is used then returns a
            Dataset object containing the corresponding DataElements.
        """
        # If passed a slice, return a Dataset containing the corresponding
        #   DataElements
        if isinstance(key, slice):
            return self._dataset_slice(key)

        if isinstance(key, BaseTag):
            tag = key
        else:
            tag = Tag(key)
        data_elem = self._dict[tag]

        if isinstance(data_elem, DataElement):
            return data_elem
        elif isinstance(data_elem, tuple):
            # If a deferred read, then go get the value now
            if data_elem.value is None:
                from pydicom.filereader import read_deferred_data_element
                data_elem = read_deferred_data_element(
                    self.fileobj_type, self.filename, self.timestamp,
                    data_elem)

            if tag != BaseTag(0x00080005):
                character_set = self.read_encoding or self._character_set
            else:
                character_set = default_encoding
            # Not converted from raw form read from file yet; do so now
            self[tag] = DataElement_from_raw(data_elem, character_set)

            # If the Element has an ambiguous VR, try to correct it
            if 'or' in self[tag].VR:
                from pydicom.filewriter import correct_ambiguous_vr_element
                self[tag] = correct_ambiguous_vr_element(
                    self[tag], self, data_elem[6])

        return self._dict.get(tag)