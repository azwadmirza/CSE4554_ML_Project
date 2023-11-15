    def get_metadata(self, request: Request) -> Dict[Text, Any]:
        """Extracts the metadata from a slack API event (https://api.slack.com/types/event).

        Args:
            request: A `Request` object that contains a slack API event in the body.

        Returns:
            Metadata extracted from the sent event payload. This includes the output channel for the response,
            and users that have installed the bot.
        """
        content_type = request.headers.get("content-type")

        # Slack API sends either a JSON-encoded or a URL-encoded body depending on the content
        if content_type == "application/json":
            # if JSON-encoded message is received
            slack_event = request.json
            event = slack_event.get("event", {})
            thread_id = event.get("thread_ts", event.get("ts"))

            return {
                "out_channel": event.get("channel"),
                "thread_id": thread_id,
                "users": slack_event.get("authed_users"),
            }

        if content_type == "application/x-www-form-urlencoded":
            # if URL-encoded message is received
            output = request.form
            payload = json.loads(output["payload"][0])
            message = payload.get("message", {})
            thread_id = message.get("thread_ts", message.get("ts"))
            return {
                "out_channel": payload.get("channel", {}).get("id"),
                "thread_id": thread_id,
                "users": payload.get("user", {}).get("id"),
            }

        return {}