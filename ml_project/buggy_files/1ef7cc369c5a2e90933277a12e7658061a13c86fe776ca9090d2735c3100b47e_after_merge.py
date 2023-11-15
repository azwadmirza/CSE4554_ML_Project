    def __new__(cls, val, encodings):
        """Return unicode string after conversion of each part
        val -- the PN value to store
        encodings -- a list of python encodings, generally found
                 from pydicom.charset.python_encodings mapping
                 of values in DICOM data element (0008,0005).
        """
        encodings = _verify_encodings(encodings)
        comps = _decode_personname(val.split(b"="), encodings)
        new_val = u"=".join(comps)

        return compat.text_type.__new__(cls, new_val)