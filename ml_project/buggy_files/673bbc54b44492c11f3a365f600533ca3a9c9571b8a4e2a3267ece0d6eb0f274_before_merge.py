    async def send_custom_json(
        self, recipient_id: Text, json_message: Dict[Text, Any], **kwargs: Any
    ) -> None:
        json_message.setdefault("channel", self.slack_channel or recipient_id)
        json_message.setdefault("as_user", True)
        await self.client.chat_postMessage(**json_message)