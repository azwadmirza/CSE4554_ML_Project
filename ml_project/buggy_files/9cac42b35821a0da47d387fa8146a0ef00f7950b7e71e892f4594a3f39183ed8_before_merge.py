    def include_in_schema(self) -> bool:
        """
        False if this is a simple field just allowing None as used in Unions/Optional.
        """
        return len(self.validators) != 1 or self.validators[0][1] != is_none_validator