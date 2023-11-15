    def response(self, f):
        flow.FlowMaster.response(self, f)
        if f:
            f.reply()
            self._process_flow(f)
        return f