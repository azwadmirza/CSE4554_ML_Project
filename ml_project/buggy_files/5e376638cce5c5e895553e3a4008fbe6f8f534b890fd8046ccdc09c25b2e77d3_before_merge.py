    def clone(self, default_value=NoDefaultSpecified, **metadata):
        """ Copy, optionally modifying default value and metadata.

        Clones the contents of this object into a new instance of the same
        class, and then modifies the cloned copy using the specified
        ``default_value`` and ``metadata``. Returns the cloned object as the
        result.

        Note that subclasses can change the signature of this method if
        needed, but should always call the 'super' method if possible.

        Parameters
        ----------
        default_value : any
            The new default value for the trait.
        **metadata : dict
            A dictionary of metadata names and corresponding values as
            arbitrary keyword arguments.

        """
        if "parent" not in metadata:
            metadata["parent"] = self

        new = self.__class__.__new__(self.__class__)
        new_dict = new.__dict__
        new_dict.update(self.__dict__)

        if "editor" in new_dict:
            del new_dict["editor"]

        if "_metadata" in new_dict:
            new._metadata = new._metadata.copy()
        else:
            new._metadata = {}

        new._metadata.update(metadata)

        if default_value is not NoDefaultSpecified:
            new.default_value = default_value
            if self.validate is not None:
                try:
                    new.default_value = self.validate(
                        None, None, default_value
                    )
                except Exception:
                    pass

        return new