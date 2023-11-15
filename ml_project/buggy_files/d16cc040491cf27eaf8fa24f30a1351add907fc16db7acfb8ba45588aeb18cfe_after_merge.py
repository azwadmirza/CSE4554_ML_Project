    def to_json(self) -> dict:
        """Transform the object to a dict

        Returns
        -------
        dict
            The case in the form of a dict

        """
        if self.moderator is None or isinstance(self.moderator, int):
            mod = self.moderator
        else:
            mod = self.moderator.id
        if self.amended_by is None or isinstance(self.amended_by, int):
            amended_by = self.amended_by
        else:
            amended_by = self.amended_by.id
        if isinstance(self.user, int):
            user_id = self.user
        else:
            user_id = self.user.id
        data = {
            "case_number": self.case_number,
            "action_type": self.action_type,
            "guild": self.guild.id,
            "created_at": self.created_at,
            "user": user_id,
            "last_known_username": self.last_known_username,
            "moderator": mod,
            "reason": self.reason,
            "until": self.until,
            "channel": self.channel.id if hasattr(self.channel, "id") else None,
            "amended_by": amended_by,
            "modified_at": self.modified_at,
            "message": self.message.id if hasattr(self.message, "id") else None,
        }
        return data