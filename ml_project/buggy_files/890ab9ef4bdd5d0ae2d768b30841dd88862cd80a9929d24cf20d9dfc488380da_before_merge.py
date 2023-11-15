    async def send_attachment(
        self, recipient_id: Text, attachment: Dict[Text, Any], **kwargs: Any
    ) -> None:
        recipient = self.slack_channel or recipient_id
        await self.client.chat_postMessage(
            channel=recipient, as_user=True, attachments=[attachment], **kwargs,
        )