    def start(self, workers=1, max_queue_size=10):
        """Start the handler's workers.

        # Arguments
            workers: number of worker threads
            max_queue_size: queue size
                (when full, workers could block on `put()`)
        """
        if self.use_multiprocessing:
            self.executor_fn = lambda seqs: multiprocessing.Pool(workers,
                                                                 initializer=init_pool,
                                                                 initargs=(seqs,))
        else:
            # We do not need the init since it's threads.
            self.executor_fn = lambda _: ThreadPool(workers)
        self.workers = workers
        self.queue = queue.Queue(max_queue_size)
        self.stop_signal = threading.Event()
        self.run_thread = threading.Thread(target=self._run)
        self.run_thread.daemon = True
        self.run_thread.start()