    def __init__(self, model, hvd_opt, num_steps=10**6):
        """Construct a new ScheduledOptimizer, which uses horovod optimizer under the hood for averaging gradients
         across all the Horovod ranks.

        Args:
            model: The training model. ByteScheduler uses the model object to register hooks.
            hvd_opt: Optimizer to use for averaging gradients and applying updates.
            num_steps: The maximum number of training steps. ByteScheduler needs to know when to stop cross-iteration
            scheduling.

        Usage example:
        ```
        import bytescheduler.pytorch.horovod as bsc
        bsc.init()
        optimizer = hvd.DistributedOptimizer(optimizer, named_parameters, compression)
        optimizer = bsc.ScheduledOptimizer(model, optimizer, num_steps)
        ```
        """
        self._model = model
        self._opt = hvd_opt
        self._logger = logging.getLogger("ByteScheduler")
        self._logger.debug("hvd size {}, rank {}".format(size(), rank()))
        self._desc = "rank {}".format(rank())

        # Track training steps
        self._step = 0
        self._final_step = num_steps

        # Use lock to block the forward propagation of each parameter.
        self._locks = {}
        for param_group in self.param_groups:
            for p in param_group['params']:
                self._locks[p] = threading.Lock()

        # The closer to input layer, the higher the priority is.
        self._priority_indexes = {}
        priority = 0
        for p in model.parameters():
            self._priority_indexes[p] = priority
            priority += 1

        assert len(self._grad_accs) == 0
        if size() > 1:
            self._register_forward_hooks()
            self._register_hooks()

        # Poll whether the tensor is ready for allreduce or whether the allreduce is finished.
        self.event_queue = queue.Queue()
        self._poller = threading.Thread(target=self._poll, args=())
        self._poller.start()

        # Let rank 0 decide the communication order.
        self._immediate = False
        self._rank = rank()
        if self._rank != 0:
            self._immediate = True

        core.start(rank=self._rank, arch="allreduce")