    def set_state(self, state):
        if 'msg_id' in state:
            msg_id = state.get('msg_id')
            if msg_id:
                self.executor.output_hook[msg_id] = self
                self.msg_id = msg_id
            else:
                del self.executor.output_hook[self.msg_id]
                self.msg_id = msg_id