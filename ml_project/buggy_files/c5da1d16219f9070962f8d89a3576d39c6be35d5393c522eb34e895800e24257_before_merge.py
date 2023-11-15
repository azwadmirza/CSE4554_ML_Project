    async def async_send_announcement(self, message, **kwargs):
        """Send announcement to the media player."""
        await self.alexa_api.send_announcement(
            message, customer_id=self._customer_id, **kwargs
        )