    def play_media(self, media_type, media_id, enqueue=None, **kwargs):
        """Send the play_media command to the media player."""
        if media_type == "music":
            self.alexa_api.send_tts("Sorry, text to speech can only be called "
                                    " with the media player alexa tts service")
        elif media_type == "sequence":
            self.alexa_api.send_sequence(media_id,
                                         customer_id=self._customer_id,
                                         **kwargs)
        elif media_type == "routine":
            self.alexa_api.run_routine(media_id)
        else:
            self.alexa_api.play_music(media_type, media_id,
                                      customer_id=self._customer_id, **kwargs)
        self.update()