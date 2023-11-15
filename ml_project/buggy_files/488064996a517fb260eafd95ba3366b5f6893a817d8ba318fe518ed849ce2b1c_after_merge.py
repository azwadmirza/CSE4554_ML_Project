    def retrieve(self, sender_id: Text) -> Optional[DialogueStateTracker]:
        """Create a tracker from all previously stored events."""
        # Retrieve dialogues for a sender_id in reverse-chronological order based on
        # the session_date sort key
        dialogues = self.db.query(
            KeyConditionExpression=Key("sender_id").eq(sender_id),
            Limit=1,
            ScanIndexForward=False,
        )["Items"]

        if not dialogues:
            return None

        events = dialogues[0].get("events", [])

        # `float`s are stored as `Decimal` objects - we need to convert them back
        events_with_floats = core_utils.replace_decimals_with_floats(events)

        return DialogueStateTracker.from_dict(
            sender_id, events_with_floats, self.domain.slots
        )