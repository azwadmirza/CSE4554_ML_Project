    def next_uri(self):
        try:
            uri = path_to_uri(self.files.next())
        except StopIteration:
            self.stop()
            return False
        self.pipe.set_state(gst.STATE_NULL)
        self.uribin.set_property('uri', uri)
        self.pipe.set_state(gst.STATE_PAUSED)
        return True