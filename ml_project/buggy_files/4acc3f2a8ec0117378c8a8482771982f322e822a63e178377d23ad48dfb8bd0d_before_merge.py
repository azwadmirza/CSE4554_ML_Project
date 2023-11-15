    def output(self, outs, msg, display_id, cell_index):
        parent_msg_id = msg['parent_header'].get('msg_id')
        if parent_msg_id in self.output_hook:
            self.output_hook[parent_msg_id].output(outs, msg, display_id, cell_index)
            return
        super(VoilaExecutePreprocessor, self).output(outs, msg, display_id, cell_index)