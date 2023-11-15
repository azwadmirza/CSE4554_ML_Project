    def __init__(self, graph_serialized, state, chunk_targets=None, data_targets=None,
                 io_meta=None, data_metas=None, mem_request=None, shared_input_chunks=None,
                 pinned_keys=None, mem_overhead_keys=None, est_finish_time=None,
                 calc_actor_uid=None, send_addresses=None, retry_delay=None,
                 finish_callbacks=None, stop_requested=False, calc_device=None,
                 preferred_data_device=None, resource_released=False,
                 no_prepare_chunk_keys=None):

        self.graph_serialized = graph_serialized
        graph = self.graph = deserialize_graph(graph_serialized)

        self._state = state
        self.state_time = time.time()
        self.data_targets = data_targets or []
        self.chunk_targets = chunk_targets or []
        self.io_meta = io_meta or dict()
        self.data_metas = data_metas or dict()
        self.shared_input_chunks = shared_input_chunks or set()
        self.mem_request = mem_request or dict()
        self.pinned_keys = set(pinned_keys or [])
        self.mem_overhead_keys = set(mem_overhead_keys or [])
        self.est_finish_time = est_finish_time or time.time()
        self.calc_actor_uid = calc_actor_uid
        self.send_addresses = send_addresses
        self.retry_delay = retry_delay or 0
        self.retry_pending = False
        self.finish_callbacks = finish_callbacks or []
        self.stop_requested = stop_requested or False
        self.calc_device = calc_device
        self.preferred_data_device = preferred_data_device
        self.resource_released = resource_released
        self.no_prepare_chunk_keys = no_prepare_chunk_keys or set()

        _, self.op_string = concat_operand_keys(graph)