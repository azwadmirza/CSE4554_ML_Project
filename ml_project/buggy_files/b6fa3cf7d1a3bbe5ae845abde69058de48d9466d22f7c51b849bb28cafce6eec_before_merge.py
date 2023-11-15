    def get_graph_state(self, session_id, graph_key):
        from .scheduler import GraphState

        graph_meta_ref = self.get_graph_meta_ref(session_id, graph_key)
        if self.actor_client.has_actor(graph_meta_ref):
            state_obj = graph_meta_ref.get_state()
            state = state_obj.value if state_obj else 'preparing'
        else:
            state = 'preparing'
        state = GraphState(state.lower())
        return state