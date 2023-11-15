    async def async_send_tts(self, message, **kwargs):
        """Send TTS to Device.

        NOTE: Does not work on WHA Groups.
        """
        self.check_login_changes()
        await self.alexa_api.send_tts(message, customer_id=self._customer_id, **kwargs)