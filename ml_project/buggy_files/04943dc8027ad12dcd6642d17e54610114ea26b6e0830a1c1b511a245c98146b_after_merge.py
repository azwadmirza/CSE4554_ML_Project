    def set_table_attributes(self, attributes):
        """
        Set the table attributes. These are the items
        that show up in the opening ``<table>`` tag in addition
        to to automatic (by default) id.

        .. versionadded:: 0.17.1

        Parameters
        ----------
        precision: int

        Returns
        -------
        self : Styler
        """
        self.table_attributes = attributes
        return self