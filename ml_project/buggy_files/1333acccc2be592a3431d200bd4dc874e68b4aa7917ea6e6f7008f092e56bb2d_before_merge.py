    def onModeChanged(self, current_mode):
        log.info('onModeChanged')
        if current_mode is openshot.PLAYBACK_PLAY:
            self.parent.SetPlayheadFollow(False)
        else:
            self.parent.SetPlayheadFollow(True)