    def __new__(cls, val, encodings):
        """Return unicode string after conversion of each part
        val -- the PN value to store
        encodings -- a list of python encodings, generally found
                 from pydicom.charset.python_encodings mapping
                 of values in DICOM data element (0008,0005).
        """
        # in here to avoid circular import
        from pydicom.charset import decode_string

        if not isinstance(encodings, list):
            encodings = [encodings]
        components = val.split(b"=")
        comps = _decode_personname(components, encodings)
        new_val = u"=".join(comps)

        return compat.text_type.__new__(cls, new_val)