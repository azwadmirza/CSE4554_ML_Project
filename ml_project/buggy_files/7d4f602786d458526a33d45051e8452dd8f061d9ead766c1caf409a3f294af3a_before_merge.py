    def delete(self, flow_id):
        self.flow.kill(self.master)
        self.state.delete_flow(self.flow)