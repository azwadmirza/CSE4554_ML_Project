    def pop(self, key, *args):
        """Emulate dictionary `pop`, but additionally support tag ID tuple
        and DICOM keyword.

        Removes the data element for `key` if it exists and returns it,
        otherwise returns a default value if given or raises `KeyError`.

        Parameters
        ----------
        key: int or str or 2-tuple
            if tuple - the group and element number of the DICOM tag
            if int - the combined group/element number
            if str - the DICOM keyword of the tag

        *args: zero or one argument
            defines the behavior if no tag exists for `key`: if given,
            it defines the return value, if not given, `KeyError` is raised

        Returns
        -------
        The data element for `key` if it exists, or the default value if given.

        Raises
        ------
        KeyError
            If the key is not a valid tag ID or keyword.
            If the tag does not exist and no default is given.
        """
        try:
            tag = Tag(key)
        except (ValueError, OverflowError):
            return self._dict.pop(key, *args)
        return self._dict.pop(tag, *args)