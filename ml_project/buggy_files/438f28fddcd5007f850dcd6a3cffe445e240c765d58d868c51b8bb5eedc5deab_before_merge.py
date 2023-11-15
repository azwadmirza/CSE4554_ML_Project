    def transpose(self, *args, **kwargs):
        """Transposes this DataManager.

        Returns:
            Transposed new DataManager.
        """
        new_data = self.data.transpose(*args, **kwargs)
        # Switch the index and columns and transpose the
        new_manager = self.__constructor__(
            new_data, self.columns, self.index, is_transposed=self._is_transposed ^ 1
        )
        return new_manager