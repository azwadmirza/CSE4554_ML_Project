    def save_as(self, filename, write_like_original=True):
        """Write the :class:`Dataset` to `filename`.

        Wrapper for pydicom.filewriter.dcmwrite, passing this dataset to it.
        See documentation for that function for details.

        See Also
        --------
        pydicom.filewriter.dcmwrite
            Write a DICOM file from a :class:`FileDataset` instance.
        """
        pydicom.dcmwrite(filename, self, write_like_original)