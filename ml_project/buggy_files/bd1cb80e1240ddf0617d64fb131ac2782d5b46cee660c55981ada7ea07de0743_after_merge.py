    async def _parse_message(self, response):
        """Handle logic to parse a received message.

        Since everyone can send a private message to any user/bot
        in Telegram, this method allows to set a list of whitelisted
        users that can interact with the bot. If any other user tries
        to interact with the bot the command is not parsed and instead
        the bot will inform that user that he is not allowed to talk
        with the bot.

        We also set self.latest_update to +1 in order to get the next
        available message (or an empty {} if no message has been received
        yet) with the method self._get_messages().

        Args:
            response (dict): Response returned by aiohttp.ClientSession.

        """
        for result in response["result"]:
            _LOGGER.debug(result)
            if "channel" in result["message"]["chat"]["type"]:
                _LOGGER.debug("Channel message parsing not supported "
                              "- Ignoring message")
            elif "message" in result and "text" in result["message"]:
                user = self.get_user(result)
                message = Message(
                    user,
                    result["message"]["chat"],
                    self,
                    result["message"]["text"])

                if self.handle_user_permission(result, user):
                    await self.opsdroid.parse(message)
                else:
                    message.text = "Sorry, you're not allowed " \
                                   "to speak with this bot."
                    await self.respond(message)
                self.latest_update = result["update_id"] + 1
            else:
                _LOGGER.error("Unable to parse the message.")