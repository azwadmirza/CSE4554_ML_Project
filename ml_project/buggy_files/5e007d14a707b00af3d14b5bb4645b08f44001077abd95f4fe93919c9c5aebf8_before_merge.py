    def dispatchStringRegex(self, update):
        """
        Dispatches an update to all string regex handlers that match the
        string.

        Args:
            command (str): The command keyword
            update (telegram.Update): The Telegram update that contains the
                command
        """

        matching_handlers = []

        for matcher in self.string_regex_handlers:
            if match(matcher, update):
                for handler in self.string_regex_handlers[matcher]:
                    matching_handlers.append(handler)

        self.dispatchTo(matching_handlers, update)