    def last_clean_details(self) -> CleaningDetails:
        """Return details from the last cleaning."""
        last_clean_id = self.clean_history().ids.pop(0)
        return self.clean_details(last_clean_id, return_list=False)