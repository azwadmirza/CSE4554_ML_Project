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
            self._kernel_reply = repr(msg)
            self.sig_got_reply.emit()
            return

        # Receive values asked for Spyder
        value = data.get('__spy_data__', None)
        if value is not None:
            if isinstance(value, CannedObject):
                value = value.get_object()
            self._kernel_value = value
            self.sig_got_reply.emit()
            return

        # Receive Pdb state and dispatch it
        pdb_state = data.get('__spy_pdb_state__', None)
        if pdb_state is not None and isinstance(pdb_state, dict):
            self.refresh_from_pdb(pdb_state)