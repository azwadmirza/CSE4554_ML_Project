    def output(self, outs, msg, display_id, cell_index):
        if self.clear_before_next_output:
            self.outputs = []
            self.clear_before_next_output = False
        self.parent_header = msg['parent_header']
        content = msg['content']
        if 'data' not in content:
            output = {"output_type": "stream", "text": content['text'], "name": content['name']}
        else:
            data = content['data']
            output = {"output_type": "display_data", "data": data, "metadata": {}}
        self.outputs.append(output)
        self.sync_state()
        if hasattr(self.executor, 'widget_state'):
            # sync the state to the nbconvert state as well, since that is used for testing
            self.executor.widget_state[self.comm_id]['outputs'] = self.outputs