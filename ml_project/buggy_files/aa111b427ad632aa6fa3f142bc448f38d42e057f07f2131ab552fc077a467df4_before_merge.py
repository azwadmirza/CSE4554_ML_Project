        async def webhook(request: Request) -> HTTPResponse:
            if request.form:
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
                    elif payload["actions"][0]["type"] == "button":
                        # link buttons don't have "value", don't send their clicks to bot
                        return response.text("User clicked link button")
                return response.text(
                    "The input message could not be processed.", status=500
                )

            elif request.json:
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

            return response.text("Bot message delivered.")