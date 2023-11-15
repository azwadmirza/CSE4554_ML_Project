    def on_error(self, error, debug):
        error_msg = str(error).decode()
        debug_msg = debug.decode()
        gst_logger.debug(
            "Got ERROR bus message: error=%r debug=%r", error_msg, debug_msg
        )
        gst_logger.error("GStreamer error: %s", error_msg)
        # TODO: is this needed?
        self._audio.stop_playback()