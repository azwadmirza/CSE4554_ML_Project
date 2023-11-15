    async def send_image_url(
        self, recipient_id: Text, image: Text, **kwargs: Any
    ) -> None:
        recipient = self.slack_channel or recipient_id
        image_block = {"type": "image", "image_url": image, "alt_text": image}

        await self._post_message(
            channel=recipient, as_user=True, text=image, blocks=[image_block],
        )