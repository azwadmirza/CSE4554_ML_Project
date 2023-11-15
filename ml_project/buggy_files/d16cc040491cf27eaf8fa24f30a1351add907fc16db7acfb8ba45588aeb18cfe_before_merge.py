    def to_json(self) -> dict:
        """Transform the object to a dict

        Returns
        -------
        dict
            The case in the form of a dict

        """
        if self.moderator is not None:
            mod = self.moderator.id
        else:
            mod = None
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
            "amended_by": self.amended_by.id if hasattr(self.amended_by, "id") else None,
            "modified_at": self.modified_at,
            "message": self.message.id if hasattr(self.message, "id") else None,
        }
        return data