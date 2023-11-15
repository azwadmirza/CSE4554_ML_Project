    def response(self, f):
        f = flow.FlowMaster.response(self, f)
        if f:
            self._process_flow(f)
        return f