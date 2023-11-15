    def _read_file(self, fname, **kwargs):
        """
        Test reading a file with sunpy.io for automatic source detection.

        Parameters
        ----------

        fname : filename

        kwargs

        Returns
        -------

        parsed :  bool
            True if file has been reading

        pairs : list or str
            List of (data, header) pairs if ``parsed`` is ``True`` or ``fname``
            if ``False``
        """
        if 'source' not in kwargs.keys() or not kwargs['source']:
            try:
                pairs = read_file(fname, **kwargs)

                new_pairs = []
                for pair in pairs:
                    filedata, filemeta = pair
                    if isinstance(filemeta, FileHeader):
                        data = filedata
                        meta = MetaDict(filemeta)
                        new_pairs.append(HDPair(data, meta))
                return True, new_pairs
            except UnrecognizedFileTypeError:
                return False, fname
        else:
            return False, fname