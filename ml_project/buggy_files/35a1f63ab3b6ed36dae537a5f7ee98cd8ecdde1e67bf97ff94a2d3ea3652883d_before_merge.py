    def insert(self, loc, column, value):
        """Insert new column data.

        Args:
            loc: Insertion index.
            column: Column labels to insert.
            value: Dtype object values to insert.

        Returns:
            A new DFAlgQueryCompiler with new data inserted.
        """
        if is_list_like(value):
            return super().insert(loc=loc, column=column, value=value)

        return self.__constructor__(self._modin_frame.insert(loc, column, value))