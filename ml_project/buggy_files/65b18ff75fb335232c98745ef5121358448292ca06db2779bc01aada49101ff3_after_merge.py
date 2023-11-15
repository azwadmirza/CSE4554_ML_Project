    def __init__(self, session_id, graph_id, op_key, op_info, worker=None, position=None):
        super(BaseOperandActor, self).__init__()
        self._session_id = session_id
        self._graph_ids = [graph_id]
        self._info = copy.deepcopy(op_info)
        self._op_key = op_key
        self._op_path = '/sessions/%s/operands/%s' % (self._session_id, self._op_key)

        self._position = position
        # worker actually assigned
        self._worker = worker

        self._op_name = op_info['op_name']
        self._state = self._last_state = OperandState(op_info['state'].lower())
        io_meta = self._io_meta = op_info['io_meta']
        self._pred_keys = io_meta['predecessors']
        self._succ_keys = io_meta['successors']

        # set of finished predecessors, used to decide whether we should move the operand to ready
        self._finish_preds = set()
        # set of finished successors, used to detect whether we can do clean up
        self._finish_succs = set()

        # handlers of states. will be called when the state of the operand switches
        # from one to another
        self._state_handlers = {
            OperandState.UNSCHEDULED: self._on_unscheduled,
            OperandState.READY: self._on_ready,
            OperandState.RUNNING: self._on_running,
            OperandState.FINISHED: self._on_finished,
            OperandState.FREED: self._on_freed,
            OperandState.FATAL: self._on_fatal,
            OperandState.CANCELLING: self._on_cancelling,
            OperandState.CANCELLED: self._on_cancelled,
        }

        self._graph_refs = []
        self._cluster_info_ref = None
        self._assigner_ref = None
        self._resource_ref = None
        self._kv_store_ref = None
        self._chunk_meta_ref = None