    def shutdown(self):
        self.unload_scripts()
        super(FlowMaster, self).shutdown()

        # Add all flows that are still active
        if self.stream:
            for i in self.state.flows:
                if not i.response:
                    self.stream.add(i)
            self.stop_stream()