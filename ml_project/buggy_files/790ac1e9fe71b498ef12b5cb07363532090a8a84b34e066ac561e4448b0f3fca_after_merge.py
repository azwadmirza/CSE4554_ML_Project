    def update(self, dictionary):
        """Extend dict.update() to handle DICOM keywords.

        Parameters
        ----------
        dictionary : dict or Dataset
            The dict or Dataset to use when updating the current object.
        """
        for key, value in list(dictionary.items()):
            if isinstance(key, (str, compat.text_type)):
                setattr(self, key, value)
            else:
                self[Tag(key)] = value