    def retrieve(self, sender_id: Text) -> Optional[DialogueStateTracker]:
        """Create a tracker from all previously stored events."""

        # Retrieve dialogues for a sender_id in reverse chronological order based on
        # the session_date sort key
        dialogues = self.db.query(
            KeyConditionExpression=Key("sender_id").eq(sender_id),
            Limit=1,
            ScanIndexForward=False,
        )["Items"]
        if dialogues:
            return DialogueStateTracker.from_dict(
                sender_id, dialogues[0].get("events"), self.domain.slots
            )
        else:
            return None