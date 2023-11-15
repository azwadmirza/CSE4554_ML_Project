    async def send_quick_replies(
        self,
        recipient_id: Text,
        text: Text,
        quick_replies: List[Dict[Text, Any]],
        **kwargs: Any
    ) -> None:
        """Sends quick replies to the output."""

        self._add_text_info(quick_replies)
        self.send(recipient_id, FBText(text=text, quick_replies=quick_replies))