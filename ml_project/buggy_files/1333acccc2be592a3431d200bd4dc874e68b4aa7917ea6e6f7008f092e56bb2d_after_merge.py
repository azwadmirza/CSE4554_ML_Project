    def onModeChanged(self, current_mode):
        log.info('onModeChanged')
        try:
            if current_mode is openshot.PLAYBACK_PLAY:
                self.parent.SetPlayheadFollow(False)
            else:
                self.parent.SetPlayheadFollow(True)
        except AttributeError:
            # Parent object doesn't need the playhead follow code
            pass