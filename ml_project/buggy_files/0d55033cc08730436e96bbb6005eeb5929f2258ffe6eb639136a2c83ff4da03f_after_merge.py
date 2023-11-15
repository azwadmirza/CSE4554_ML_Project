    async def process_message(self, **payload):
        """Process a raw message and pass it to the parser."""
        message = payload["data"]

        # Ignore message edits
        if "subtype" in message and message["subtype"] == "message_changed":
            return

        # Ignore own messages
        if (
            "subtype" in message
            and message["subtype"] == "bot_message"
            and message["bot_id"] == self.bot_id
        ):
            return

        # Lookup username
        _LOGGER.debug(_("Looking up sender username"))
        try:
            user_info = await self.lookup_username(message["user"])
        except ValueError:
            return

        # Replace usernames in the message
        _LOGGER.debug(_("Replacing userids in message with usernames"))
        message["text"] = await self.replace_usernames(message["text"])

        await self.opsdroid.parse(
            Message(
                message["text"],
                user_info["name"],
                message["channel"],
                self,
                raw_event=message,
            )
        )