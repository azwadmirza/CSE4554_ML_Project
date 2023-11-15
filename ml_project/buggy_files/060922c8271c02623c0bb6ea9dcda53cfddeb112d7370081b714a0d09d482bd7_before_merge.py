    def on_warning(self, error, debug):
        error_msg = str(error).decode()
        debug_msg = debug.decode()
        gst_logger.warning("GStreamer warning: %s", error_msg)
        gst_logger.debug(
            "Got WARNING bus message: error=%r debug=%r", error_msg, debug_msg
        )