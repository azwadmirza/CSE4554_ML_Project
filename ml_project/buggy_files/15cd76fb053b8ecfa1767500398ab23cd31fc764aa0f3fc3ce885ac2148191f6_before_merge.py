    def _handle_data_message(self, msg):
        """
        Handle raw (serialized) data sent by the kernel

        We only handle data asked by Spyder, in case people use
        publish_data for other purposes.
        """
        # Deserialize data
        try:
            data = deserialize_object(msg['buffers'])[0]
        except Exception as msg:
            self._kernel_value = None
            self._kernel_reply = msg
            self.sig_get_value.emit()
            return

        # We only handle data asked by Spyder
        value = data.get('__spy_data__', None)
        if value is not None:
            if isinstance(value, CannedObject):
                value = value.get_object()
            self._kernel_value = value
            self.sig_get_value.emit()