    def on_stream_start(self):
        gst_logger.debug('Got STREAM_START bus message')
        uri = self._audio._pending_uri
        logger.debug('Audio event: stream_changed(uri=%r)', uri)
        AudioListener.send('stream_changed', uri=uri)

        # Emit any postponed tags that we got after about-to-finish.
        tags, self._audio._pending_tags = self._audio._pending_tags, None
        self._audio._tags = tags

        if tags:
            logger.debug('Audio event: tags_changed(tags=%r)', tags.keys())
            AudioListener.send('tags_changed', tags=tags.keys())