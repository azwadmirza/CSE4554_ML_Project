    def request(self, f):
        f = flow.FlowMaster.request(self, f)
        if f:
            self.state.delete_flow(f)
        return f