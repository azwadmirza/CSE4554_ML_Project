    async def send_custom_json(
        self, recipient_id: Text, json_message: Dict[Text, Any], **kwargs: Any
    ) -> None:
        """Send custom json dict"""

        json_message.setdefault("to", recipient_id)
        if not json_message.get("media_url"):
            json_message.setdefault("body", "")
        if not json_message.get("messaging_service_sid"):
            json_message.setdefault("from", self.twilio_number)

        await self._send_message(json_message)