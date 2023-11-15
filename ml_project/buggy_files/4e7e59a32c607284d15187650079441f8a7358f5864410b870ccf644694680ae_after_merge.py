    def dir(self, *filters):
        """Return an alphabetical list of DataElement keywords in the Dataset.

        Intended mainly for use in interactive Python sessions. Only lists the
        DataElement keywords in the current level of the Dataset (i.e. the
        contents of any Sequence elements are ignored).

        Parameters
        ----------
        filters : str
            Zero or more string arguments to the function. Used for
            case-insensitive match to any part of the DICOM keyword.

        Returns
        -------
        list of str
            The matching DataElement keywords in the dataset. If no filters are
            used then all DataElement keywords are returned.
        """
        allnames = [keyword_for_tag(tag) for tag in self._dict.keys()]
        # remove blanks - tags without valid names (e.g. private tags)
        allnames = [x for x in allnames if x]
        # Store found names in a dict, so duplicate names appear only once
        matches = {}
        for filter_ in filters:
            filter_ = filter_.lower()
            match = [x for x in allnames if x.lower().find(filter_) != -1]
            matches.update(dict([(x, 1) for x in match]))
        if filters:
            names = sorted(matches.keys())
            return names
        else:
            return sorted(allnames)