    def unsubscribe(self, tag, match_type=None):
        """
        Un-subscribe to events matching the passed tag.
        """
        if tag is None:
            return
        match_func = self._get_match_func(match_type)

        try:
            self.pending_tags.remove([tag, match_func])
        except ValueError:
            pass

        old_events = self.pending_events
        self.pending_events = []
        for evt in old_events:
            if any(
                pmatch_func(evt["tag"], ptag) for ptag, pmatch_func in self.pending_tags
            ):
                self.pending_events.append(evt)