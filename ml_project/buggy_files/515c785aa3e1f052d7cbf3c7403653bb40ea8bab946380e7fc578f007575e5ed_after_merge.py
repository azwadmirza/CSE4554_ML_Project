    def init_custom(self, group_identifier: str, identifier_count: int):
        """
        Initializes a custom group for usage. This method must be called first!
        """
        if identifier_count != self.custom_groups.setdefault(group_identifier, identifier_count):
            raise ValueError(
                f"Cannot change identifier count of already registered group: {group_identifier}"
            )