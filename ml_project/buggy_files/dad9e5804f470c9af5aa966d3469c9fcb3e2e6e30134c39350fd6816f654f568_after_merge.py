    def add_new(self, tag, VR, value):
        """Add a DataElement to the Dataset.

        Parameters
        ----------
        tag
            The DICOM (group, element) tag in any form accepted by
            pydicom.tag.Tag such as [0x0010, 0x0010], (0x10, 0x10), 0x00100010,
            etc.
        VR : str
            The 2 character DICOM value representation (see DICOM standard part
            5, Section 6.2).
        value
            The value of the data element. One of the following:
            * a single string or number
            * a list or tuple with all strings or all numbers
            * a multi-value string with backslash separator
            * for a sequence DataElement, an empty list or list of Dataset
        """
        data_element = DataElement(tag, VR, value)
        # use data_element.tag since DataElement verified it
        self._dict[data_element.tag] = data_element