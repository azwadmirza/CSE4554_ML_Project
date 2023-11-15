    def init_custom(self, group_identifier: str, identifier_count: int):
        """
        Initializes a custom group for usage. This method must be called first!
        """
        if group_identifier in self.custom_groups:
            raise ValueError(f"Group identifier already registered: {group_identifier}")

        self.custom_groups[group_identifier] = identifier_count