    def __init__(
        self,
        hook: "FrameworkHook",
        id: Union[int, str] = 0,
        data: Union[List, tuple] = None,
        is_client_worker: bool = False,
        log_msgs: bool = False,
        verbose: bool = False,
        auto_add: bool = True,
        message_pending_time: Union[int, float] = 0,
    ):
        """Initializes a BaseWorker."""
        super().__init__()
        self.hook = hook

        self.object_store = ObjectStore(owner=self)

        self.id = id
        self.is_client_worker = is_client_worker
        self.log_msgs = log_msgs
        self.verbose = verbose
        self.auto_add = auto_add
        self._message_pending_time = message_pending_time
        self.msg_history = list()

        # For performance, we cache all possible message types
        self._message_router = {
            TensorCommandMessage: self.execute_tensor_command,
            PlanCommandMessage: self.execute_plan_command,
            WorkerCommandMessage: self.execute_worker_command,
            ObjectMessage: self.handle_object_msg,
            ObjectRequestMessage: self.respond_to_obj_req,
            ForceObjectDeleteMessage: self.handle_delete_object_msg,  # FIXME: there is no ObjectDeleteMessage
            ForceObjectDeleteMessage: self.handle_force_delete_object_msg,
            IsNoneMessage: self.is_object_none,
            GetShapeMessage: self.handle_get_shape_message,
            SearchMessage: self.respond_to_search,
        }

        self._plan_command_router = {
            codes.PLAN_CMDS.FETCH_PLAN: self._fetch_plan_remote,
            codes.PLAN_CMDS.FETCH_PROTOCOL: self._fetch_protocol_remote,
        }

        self.load_data(data)

        # Declare workers as appropriate
        self._known_workers = {}
        if auto_add:
            if hook is not None and hook.local_worker is not None:
                known_workers = self.hook.local_worker._known_workers
                if self.id in known_workers:
                    if isinstance(known_workers[self.id], type(self)):
                        # If a worker with this id already exists and it has the
                        # same type as the one being created, we copy all the attributes
                        # of the existing worker to this one.
                        self.__dict__.update(known_workers[self.id].__dict__)
                    else:
                        raise RuntimeError(
                            "Worker initialized with the same id and different types."
                        )
                else:
                    hook.local_worker.add_worker(self)
                    for worker_id, worker in hook.local_worker._known_workers.items():
                        if worker_id not in self._known_workers:
                            self.add_worker(worker)
                        if self.id not in worker._known_workers:
                            worker.add_worker(self)
            else:
                # Make the local worker aware of itself
                # self is the to-be-created local worker
                self.add_worker(self)

        if hook is None:
            self.framework = None
        else:
            # TODO[jvmancuso]: avoid branching here if possible, maybe by changing code in
            #     execute_tensor_command or command_guard to not expect an attribute named "torch"
            #     (#2530)
            self.framework = hook.framework
            if hasattr(hook, "torch"):
                self.torch = self.framework
                self.remote = Remote(self, "torch")
            elif hasattr(hook, "tensorflow"):
                self.tensorflow = self.framework
                self.remote = Remote(self, "tensorflow")

        # storage object for crypto primitives
        self.crypto_store = PrimitiveStorage(owner=self)