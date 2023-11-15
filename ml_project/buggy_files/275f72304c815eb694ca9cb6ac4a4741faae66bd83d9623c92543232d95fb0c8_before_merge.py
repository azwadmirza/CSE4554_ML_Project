    def save_as(self, filename, write_like_original=True):
        """Write the :class:`Dataset` to `filename`.

        Saving requires that the ``Dataset.is_implicit_VR`` and
        ``Dataset.is_little_endian`` attributes exist and are set
        appropriately. If ``Dataset.file_meta.TransferSyntaxUID`` is present
        then it should be set to a consistent value to ensure conformance.

        **Conformance with DICOM File Format**

        If `write_like_original` is ``False``, the :class:`Dataset` will be
        stored in the :dcm:`DICOM File Format <part10/chapter_7.html>`. To do
        so requires that the ``Dataset.file_meta`` attribute
        exists and contains a :class:`Dataset` with the required (Type 1) *File
        Meta Information Group* elements (see
        :func:`~pydicom.filewriter.dcmwrite` and
        :func:`~pydicom.filewriter.write_file_meta_info` for more information).

        If `write_like_original` is ``True`` then the :class:`Dataset` will be
        written as is (after minimal validation checking) and may or may not
        contain all or parts of the *File Meta Information* (and hence may or
        may not be conformant with the DICOM File Format).

        Parameters
        ----------
        filename : str or PathLike or file-like
            Name of file or the file-like to write the new DICOM file to.
        write_like_original : bool, optional
            If ``True`` (default), preserves the following information from
            the :class:`Dataset` (and may result in a non-conformant file):

            - preamble -- if the original file has no preamble then none will
              be written.
            - file_meta -- if the original file was missing any required *File
              Meta Information Group* elements then they will not be added or
              written.
              If (0002,0000) *File Meta Information Group Length* is present
              then it may have its value updated.
            - seq.is_undefined_length -- if original had delimiters, write them
              now too, instead of the more sensible length characters
            - is_undefined_length_sequence_item -- for datasets that belong to
              a sequence, write the undefined length delimiters if that is
              what the original had.

            If ``False``, produces a file conformant with the DICOM File
            Format, with explicit lengths for all elements.

        See Also
        --------
        pydicom.filewriter.write_dataset
            Write a :class:`Dataset` to a file.
        pydicom.filewriter.write_file_meta_info
            Write the *File Meta Information Group* elements to a file.
        pydicom.filewriter.dcmwrite
            Write a DICOM file from a :class:`FileDataset` instance.
        """
        # Ensure is_little_endian and is_implicit_VR are set
        if None in (self.is_little_endian, self.is_implicit_VR):
            has_tsyntax = False
            try:
                tsyntax = self.file_meta.TransferSyntaxUID
                if not tsyntax.is_private:
                    self.is_little_endian = tsyntax.is_little_endian
                    self.is_implicit_VR = tsyntax.is_implicit_VR
                    has_tsyntax = True
            except AttributeError:
                pass

            if not has_tsyntax:
                raise AttributeError(
                    "'{0}.is_little_endian' and '{0}.is_implicit_VR' must be "
                    "set appropriately before saving."
                    .format(self.__class__.__name__)
                )

        # Try and ensure that `is_undefined_length` is set correctly
        try:
            tsyntax = self.file_meta.TransferSyntaxUID
            if not tsyntax.is_private:
                self['PixelData'].is_undefined_length = tsyntax.is_compressed
        except (AttributeError, KeyError):
            pass

        pydicom.dcmwrite(filename, self, write_like_original)