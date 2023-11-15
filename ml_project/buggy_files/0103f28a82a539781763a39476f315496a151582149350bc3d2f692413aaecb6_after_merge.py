    def on_error(self, error, debug):
        gst_logger.error(f"GStreamer error: {error.message}")
        gst_logger.debug(
            f"Got ERROR bus message: error={error!r} debug={debug!r}"
        )

        # TODO: is this needed?
        self._audio.stop_playback()