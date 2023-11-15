    def get(self, session_id, graph_key):
        from ..scheduler.utils import GraphState

        state = self.web_api.get_graph_state(session_id, graph_key)
        if state == GraphState.RUNNING:
            self.write(json.dumps(dict(state='running')))
        elif state == GraphState.SUCCEEDED:
            self.write(json.dumps(dict(state='success')))
        elif state == GraphState.FAILED:
            self.write(json.dumps(dict(state='failed')))
        elif state == GraphState.CANCELLED:
            self.write(json.dumps(dict(state='cancelled')))
        elif state == GraphState.CANCELLING:
            self.write(json.dumps(dict(state='cancelling')))
        elif state == GraphState.PREPARING:
            self.write(json.dumps(dict(state='preparing')))