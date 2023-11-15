    def on_playbin_state_changed(self, old_state, new_state, pending_state):
        gst_logger.debug(
            'Got STATE_CHANGED bus message: old=%s new=%s pending=%s',
            old_state.value_name, new_state.value_name,
            pending_state.value_name)

        if new_state == Gst.State.READY and pending_state == Gst.State.NULL:
            # XXX: We're not called on the last state change when going down to
            # NULL, so we rewrite the second to last call to get the expected
            # behavior.
            new_state = Gst.State.NULL
            pending_state = Gst.State.VOID_PENDING

        if pending_state != Gst.State.VOID_PENDING:
            return  # Ignore intermediate state changes

        if new_state == Gst.State.READY:
            return  # Ignore READY state as it's GStreamer specific

        new_state = _GST_STATE_MAPPING[new_state]
        old_state, self._audio.state = self._audio.state, new_state

        target_state = _GST_STATE_MAPPING.get(self._audio._target_state)
        if target_state is None:
            # XXX: Workaround for #1430, to be fixed properly by #1222.
            logger.debug('Race condition happened. See #1222 and #1430.')
            return
        if target_state == new_state:
            target_state = None

        logger.debug('Audio event: state_changed(old_state=%s, new_state=%s, '
                     'target_state=%s)', old_state, new_state, target_state)
        AudioListener.send('state_changed', old_state=old_state,
                           new_state=new_state, target_state=target_state)
        if new_state == PlaybackState.STOPPED:
            logger.debug('Audio event: stream_changed(uri=None)')
            AudioListener.send('stream_changed', uri=None)

        if 'GST_DEBUG_DUMP_DOT_DIR' in os.environ:
            Gst.debug_bin_to_dot_file(
                self._audio._playbin, Gst.DebugGraphDetails.ALL, 'mopidy')