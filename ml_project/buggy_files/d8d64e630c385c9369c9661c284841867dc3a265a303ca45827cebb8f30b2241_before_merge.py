    def request(self, f):
        flow.FlowMaster.request(self, f)
        self.state.delete_flow(f)
        if f:
            f.reply()
        return f