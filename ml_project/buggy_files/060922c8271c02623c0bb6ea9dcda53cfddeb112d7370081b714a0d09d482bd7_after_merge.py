    def on_warning(self, error, debug):
        gst_logger.warning(f"GStreamer warning: {error.message}")
        gst_logger.debug(
            f"Got WARNING bus message: error={error!r} debug={debug!r}"
        )