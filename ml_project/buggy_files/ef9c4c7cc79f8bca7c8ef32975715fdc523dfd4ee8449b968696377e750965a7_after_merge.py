    async def async_play_media(self, media_type, media_id, enqueue=None, **kwargs):
        # pylint: disable=unused-argument
        """Send the play_media command to the media player."""
        self.check_login_changes()
        if media_type == "music":
            await self.async_send_tts(
                "Sorry, text to speech can only be called"
                " with the notify.alexa_media service."
                " Please see the alexa_media wiki for details."
            )
            _LOGGER.warning(
                "Sorry, text to speech can only be called"
                " with the notify.alexa_media service."
                " Please see the alexa_media wiki for details."
                "https://github.com/custom-components/alexa_media_player/wiki/Configuration%3A-Notification-Component#use-the-notifyalexa_media-service"
            )
        elif media_type == "sequence":
            await self.alexa_api.send_sequence(
                media_id,
                customer_id=self._customer_id,
                queue_delay=self.hass.data[DATA_ALEXAMEDIA]["accounts"][self.email][
                    "options"
                ].get(CONF_QUEUE_DELAY, DEFAULT_QUEUE_DELAY),
                **kwargs,
            )
        elif media_type == "routine":
            await self.alexa_api.run_routine(
                media_id,
                queue_delay=self.hass.data[DATA_ALEXAMEDIA]["accounts"][self.email][
                    "options"
                ].get(CONF_QUEUE_DELAY, DEFAULT_QUEUE_DELAY),
            )
        elif media_type == "sound":
            await self.alexa_api.play_sound(
                media_id,
                customer_id=self._customer_id,
                queue_delay=self.hass.data[DATA_ALEXAMEDIA]["accounts"][self.email][
                    "options"
                ].get(CONF_QUEUE_DELAY, DEFAULT_QUEUE_DELAY),
                **kwargs,
            )
        elif media_type == "skill":
            await self.alexa_api.run_skill(
                media_id,
                queue_delay=self.hass.data[DATA_ALEXAMEDIA]["accounts"][self.email][
                    "options"
                ].get(CONF_QUEUE_DELAY, DEFAULT_QUEUE_DELAY),
            )
        else:
            await self.alexa_api.play_music(
                media_type,
                media_id,
                customer_id=self._customer_id,
                queue_delay=self.hass.data[DATA_ALEXAMEDIA]["accounts"][self.email][
                    "options"
                ].get(CONF_QUEUE_DELAY, DEFAULT_QUEUE_DELAY),
                **kwargs,
            )
        if not (
            self.hass.data[DATA_ALEXAMEDIA]["accounts"][self._login.email]["websocket"]
        ):
            await self.async_update()