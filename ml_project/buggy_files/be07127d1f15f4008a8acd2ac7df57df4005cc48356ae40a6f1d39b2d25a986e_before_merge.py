    async def send_text_message(
        self, recipient_id: Text, text: Text, **kwargs: Any
    ) -> None:
        recipient = self.slack_channel or recipient_id
        for message_part in text.strip().split("\n\n"):
            await self.client.chat_postMessage(
                channel=recipient, as_user=True, text=message_part, type="mrkdwn",
            )