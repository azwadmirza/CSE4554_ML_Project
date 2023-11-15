    def last_clean_details(self) -> Optional[CleaningDetails]:
        """Return details from the last cleaning.

        Returns None if there has been no cleanups."""
        history = self.clean_history()
        if not history.ids:
            return None

        last_clean_id = history.ids.pop(0)
        return self.clean_details(last_clean_id, return_list=False)