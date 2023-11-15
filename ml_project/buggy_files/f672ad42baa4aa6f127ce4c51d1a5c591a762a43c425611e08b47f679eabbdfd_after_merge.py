    def blueprint(
        self, on_new_message: Callable[[UserMessage], Awaitable[Any]]
    ) -> Blueprint:
        slack_webhook = Blueprint("slack_webhook", __name__)

        @slack_webhook.route("/", methods=["GET"])
        async def health(_: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @slack_webhook.route("/webhook", methods=["GET", "POST"])
        async def webhook(request: Request) -> HTTPResponse:
            content_type = request.headers.get("content-type")
            # Slack API sends either a JSON-encoded or a URL-encoded body depending on the content

            if content_type == "application/json":
                # if JSON-encoded message is received
                output = request.json
                event = output.get("event", {})
                user_message = event.get("text", "")
                sender_id = event.get("user", "")
                metadata = self.get_metadata(request)

                if "challenge" in output:
                    return response.json(output.get("challenge"))

                elif self._is_user_message(output) and self._is_supported_channel(
                    output, metadata
                ):
                    return await self.process_message(
                        request,
                        on_new_message,
                        text=self._sanitize_user_message(
                            user_message, metadata["users"]
                        ),
                        sender_id=sender_id,
                        metadata=metadata,
                    )
                else:
                    logger.warning(
                        f"Received message on unsupported channel: {metadata['out_channel']}"
                    )

            elif content_type == "application/x-www-form-urlencoded":
                # if URL-encoded message is received
                output = request.form
                payload = json.loads(output["payload"][0])

                if self._is_interactive_message(payload):
                    sender_id = payload["user"]["id"]
                    text = self._get_interactive_response(payload["actions"][0])
                    if text is not None:
                        metadata = self.get_metadata(request)
                        return await self.process_message(
                            request, on_new_message, text, sender_id, metadata
                        )
                    if payload["actions"][0]["type"] == "button":
                        # link buttons don't have "value", don't send their clicks to bot
                        return response.text("User clicked link button")
                return response.text(
                    "The input message could not be processed.", status=500
                )

            return response.text("Bot message delivered.")

        return slack_webhook