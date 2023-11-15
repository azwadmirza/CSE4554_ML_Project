    async def respond(self, message, room=None):
        """Respond with a message.

        Args:
            message (object): An instance of Message.
            room (string, optional): Name of the room to respond to.

        """
        _LOGGER.debug("Responding with: %s", message.text)

        data = dict()
        data["chat_id"] = message.room["id"]
        data["text"] = message.text
        resp = await self.session.post(self.build_url("sendMessage"),
                                       data=data)
        if resp.status == 200:
            _LOGGER.debug("Successfully responded")
        else:
            _LOGGER.error("Unable to respond.")