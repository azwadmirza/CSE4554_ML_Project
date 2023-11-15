    def __init__(self,
                 tag,
                 VR,
                 value,
                 file_value_tell=None,
                 is_undefined_length=False,
                 already_converted=False):
        """Create a new DataElement.

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
            * a single string value
            * a number
            * a list or tuple with all strings or all numbers
            * a multi-value string with backslash separator
        file_value_tell : int or None
            Used internally by Dataset to store the write position for the
            ReplaceDataElementValue() method. Default is None.
        is_undefined_length : bool
            Used internally to store whether the length field for this element
            was 0xFFFFFFFFL, i.e. 'undefined length'. Default is False.
        already_converted : bool
            Used to determine whether or not `value` requires conversion to a
            value with VM > 1. Default is False.
        """
        if not isinstance(tag, BaseTag):
            tag = Tag(tag)
        self.tag = tag

        # a known tag shall only have the VR 'UN' if it has a length that
        # exceeds the size that can be encoded in 16 bit - all other cases
        # can be seen as an encoding error and can be corrected
        if VR == 'UN' and (is_undefined_length or value is None or
                           len(value) < 0xffff):
            try:
                VR = dictionary_VR(tag)
            except KeyError:
                pass

        self.VR = VR  # Note!: you must set VR before setting value
        if already_converted:
            self._value = value
        else:
            self.value = value  # calls property setter which will convert
        self.file_tell = file_value_tell
        self.is_undefined_length = is_undefined_length