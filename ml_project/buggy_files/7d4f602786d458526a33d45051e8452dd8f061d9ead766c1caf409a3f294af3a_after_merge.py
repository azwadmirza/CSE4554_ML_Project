    def delete(self, flow_id):
        if not self.flow.reply.acked:
            self.flow.kill(self.master)
        self.state.delete_flow(self.flow)