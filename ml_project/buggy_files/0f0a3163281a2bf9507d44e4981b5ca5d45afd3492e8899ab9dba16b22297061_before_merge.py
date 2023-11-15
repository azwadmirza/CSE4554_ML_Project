    def push(self, buffer_):
        if buffer_ is None:
            gst_logger.debug('Sending appsrc end-of-stream event.')
            return self._source.emit('end-of-stream') == gst.FLOW_OK
        else:
            return self._source.emit('push-buffer', buffer_) == gst.FLOW_OK