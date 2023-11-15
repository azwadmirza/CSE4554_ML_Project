    def get_metadata(self, request: Request) -> Dict[Text, Any]:
        """Extracts the metadata from a slack API event (https://api.slack.com/types/event).

        Args:
            request: A `Request` object that contains a slack API event in the body.

        Returns:
            Metadata extracted from the sent event payload. This includes the output channel for the response,
            and users that have installed the bot.
        """
        slack_event = request.json
        event = slack_event.get("event", {})

        return {
            "out_channel": event.get("channel"),
            "users": slack_event.get("authed_users"),
        }