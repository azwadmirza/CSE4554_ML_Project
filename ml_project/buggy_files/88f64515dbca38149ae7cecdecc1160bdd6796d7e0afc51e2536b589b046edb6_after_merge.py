    def __init__(self, session_id, graph_key, serialized_tensor_graph,
                 target_tensors=None, serialized_chunk_graph=None,
                 state=GraphState.UNSCHEDULED, final_state=None):
        super(GraphActor, self).__init__()
        self._graph_key = graph_key
        self._session_id = session_id
        self._serialized_tensor_graph = serialized_tensor_graph
        self._serialized_chunk_graph = serialized_chunk_graph
        self._state = state
        self._final_state = final_state

        self._start_time = None
        self._end_time = None
        self._nodes_num = None

        self._cluster_info_ref = None
        self._assigner_actor_ref = None
        self._resource_actor_ref = None
        self._kv_store_ref = None
        self._chunk_meta_ref = None
        self._graph_meta_ref = None

        self._tensor_graph_cache = None
        self._chunk_graph_cache = None

        self._op_key_to_chunk = defaultdict(list)

        self._resource_actor = None
        self._tensor_key_opid_to_tiled = defaultdict(list)
        self._tensor_key_to_opid = dict()
        self._terminal_chunk_op_tensor = defaultdict(set)
        self._terminated_tensors = set()
        self._operand_infos = dict()
        if target_tensors:
            self._target_tensor_chunk_ops = dict((k, set()) for k in target_tensors)
            self._target_tensor_finished = dict((k, set()) for k in self._target_tensor_chunk_ops)
        else:
            self._target_tensor_chunk_ops = dict()
            self._target_tensor_finished = dict()