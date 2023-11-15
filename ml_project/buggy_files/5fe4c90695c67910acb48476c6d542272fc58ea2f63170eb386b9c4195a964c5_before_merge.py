    def actionJumpEnd_trigger(self, checked=True):
        log.info("actionJumpEnd_trigger")

        # Determine last frame (based on clips) & seek there
        max_frame = get_app().window.timeline_sync.timeline.GetMaxFrame()
        self.SeekSignal.emit(max_frame)