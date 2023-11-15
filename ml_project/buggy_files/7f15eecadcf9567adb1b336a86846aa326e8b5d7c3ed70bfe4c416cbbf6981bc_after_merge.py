    def __delattr__(self, name):
        """Intercept requests to delete an attribute by `name`.

        If `name` is a DICOM keyword:
            Delete the corresponding DataElement from the Dataset.
            >>> del ds.PatientName
        Else:
            Delete the class attribute as any other class would do.
            >>> del ds._is_some_attribute

        Parameters
        ----------
        name : str
            The keyword for the DICOM element or the class attribute to delete.
        """
        # First check if a valid DICOM keyword and if we have that data element
        tag = tag_for_keyword(name)
        if tag is not None and tag in self._dict:
            del self._dict[tag]
        # If not a DICOM name in this dataset, check for regular instance name
        #   can't do delete directly, that will call __delattr__ again
        elif name in self.__dict__:
            del self.__dict__[name]
        # Not found, raise an error in same style as python does
        else:
            raise AttributeError(name)