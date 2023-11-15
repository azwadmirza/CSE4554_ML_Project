    def walk(self, callback, recursive=True):
        """Iterate through the DataElements and run `callback` on each.

        Visit all DataElements, possibly recursing into sequences and their
        datasets. The callback function is called for each DataElement
        (including SQ element). Can be used to perform an operation on certain
        types of DataElements. E.g., `remove_private_tags`() finds all private
        tags and deletes them. DataElement`s will come back in DICOM order (by
        increasing tag number within their dataset).

        Parameters
        ----------
        callback
            A callable that takes two arguments:
                * a Dataset
                * a DataElement belonging to that Dataset
        recursive : bool
            Flag to indicate whether to recurse into Sequences.
        """
        taglist = sorted(self.tags.keys())
        for tag in taglist:

            with tag_in_exception(tag):
                data_element = self[tag]
                callback(self, data_element)  # self = this Dataset
                # 'tag in self' below needed in case callback deleted
                # data_element
                if recursive and tag in self and data_element.VR == "SQ":
                    sequence = data_element.value
                    for dataset in sequence:
                        dataset.walk(callback)