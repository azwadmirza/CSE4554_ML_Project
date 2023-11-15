    def _get_current_roles(self, trans, library_dataset):
        """
        Find all roles currently connected to relevant permissions
        on the library dataset and the underlying dataset.

        :param  library_dataset:      the model object
        :type   library_dataset:      LibraryDataset

        :rtype:     dictionary
        :returns:   dict of current roles for all available permission types
        """
        return self.serialize_dataset_association_roles(library_dataset)