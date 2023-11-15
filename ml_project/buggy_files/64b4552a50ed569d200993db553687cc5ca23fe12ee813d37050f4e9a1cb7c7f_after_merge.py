    def __getitem__(self, key):
        """
        Arg:
            key (int): index of the bit/qubit to be retrieved.

        Returns:
            tuple[Register, int]: a tuple in the form `(self, key)`.

        Raises:
            QISKitError: if the `key` is not an integer.
            QISKitIndexError: if the `key` is not in the range
                `(0, self.size)`.
        """
        if not isinstance(key, int):
            raise QISKitError("expected integer index into register")
        self.check_range(key)
        return self, key