    def _collect_internal(self) -> None:
        events = self.event_filter.get_new_entries()
        for event in events:
            self._event_occurred(event)