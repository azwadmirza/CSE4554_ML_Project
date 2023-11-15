    def start(self, poll_period=None):
        """ Start the NeedNameQeueu

        Parameters:
        ----------

        TODO: Move task receiving to a thread
        """
        logger.info("Incoming ports bound")

        if poll_period is None:
            poll_period = self.poll_period

        start = time.time()
        count = 0

        self._kill_event = threading.Event()
        self._task_puller_thread = threading.Thread(target=self.migrate_tasks_to_internal,
                                                    args=(self._kill_event,))
        self._task_puller_thread.start()

        self._command_thread = threading.Thread(target=self._command_server,
                                                args=(self._kill_event,))
        self._command_thread.start()

        poller = zmq.Poller()
        # poller.register(self.task_incoming, zmq.POLLIN)
        poller.register(self.task_outgoing, zmq.POLLIN)
        poller.register(self.results_incoming, zmq.POLLIN)

        # These are managers which we should examine in an iteration
        # for scheduling a job (or maybe any other attention?).
        # Anything altering the state of the manager should add it
        # onto this list.
        interesting_managers = set()

        while not self._kill_event.is_set():
            self.socks = dict(poller.poll(timeout=poll_period))

            # Listen for requests for work
            if self.task_outgoing in self.socks and self.socks[self.task_outgoing] == zmq.POLLIN:
                logger.debug("[MAIN] starting task_outgoing section")
                message = self.task_outgoing.recv_multipart()
                manager = message[0]

                if manager not in self._ready_manager_queue:
                    reg_flag = False

                    try:
                        msg = json.loads(message[1].decode('utf-8'))
                        msg['reg_time'] = datetime.datetime.strptime(msg['reg_time'], "%Y-%m-%d %H:%M:%S")
                        reg_flag = True
                    except Exception:
                        logger.warning("[MAIN] Got Exception reading registration message from manager:{}".format(
                            manager), exc_info=True)
                        logger.debug("[MAIN] Message :\n{}\n".format(message[0]))

                    # By default we set up to ignore bad nodes/registration messages.
                    self._ready_manager_queue[manager] = {'last': time.time(),
                                                          'free_capacity': 0,
                                                          'block_id': None,
                                                          'max_capacity': 0,
                                                          'worker_count': 0,
                                                          'active': True,
                                                          'tasks': []}
                    if reg_flag is True:
                        interesting_managers.add(manager)
                        logger.info("[MAIN] Adding manager: {} to ready queue".format(manager))
                        self._ready_manager_queue[manager].update(msg)
                        logger.info("[MAIN] Registration info for manager {}: {}".format(manager, msg))
                        if self.monitoring_enabled:
                            logger.info("Sending message {} to hub".format(self._ready_manager_queue[manager]))
                            self.hub_channel.send_pyobj((MessageType.NODE_INFO, self._ready_manager_queue[manager]))

                        if (msg['python_v'].rsplit(".", 1)[0] != self.current_platform['python_v'].rsplit(".", 1)[0] or
                            msg['parsl_v'] != self.current_platform['parsl_v']):
                            logger.warn("[MAIN] Manager {} has incompatible version info with the interchange".format(manager))

                            if self.suppress_failure is False:
                                logger.debug("Setting kill event")
                                self._kill_event.set()
                                e = ManagerLost(manager, self._ready_manager_queue[manager]['hostname'])
                                result_package = {'task_id': -1, 'exception': serialize_object(e)}
                                pkl_package = pickle.dumps(result_package)
                                self.results_outgoing.send(pkl_package)
                                logger.warning("[MAIN] Sent failure reports, unregistering manager")
                            else:
                                logger.debug("[MAIN] Suppressing shutdown due to version incompatibility")
                        else:
                            logger.info("[MAIN] Manager {} has compatible Parsl version {}".format(manager, msg['parsl_v']))
                            logger.info("[MAIN] Manager {} has compatible Python version {}".format(manager,
                                                                                                    msg['python_v'].rsplit(".", 1)[0]))
                    else:
                        # Registration has failed.
                        if self.suppress_failure is False:
                            self._kill_event.set()
                            e = BadRegistration(manager, critical=True)
                            result_package = {'task_id': -1, 'exception': serialize_object(e)}
                            pkl_package = pickle.dumps(result_package)
                            self.results_outgoing.send(pkl_package)
                        else:
                            logger.debug("[MAIN] Suppressing bad registration from manager:{}".format(
                                manager))

                else:
                    tasks_requested = int.from_bytes(message[1], "little")
                    self._ready_manager_queue[manager]['last'] = time.time()
                    if tasks_requested == HEARTBEAT_CODE:
                        logger.debug("[MAIN] Manager {} sent heartbeat".format(manager))
                        self.task_outgoing.send_multipart([manager, b'', PKL_HEARTBEAT_CODE])
                    else:
                        logger.debug("[MAIN] Manager {} requested {} tasks".format(manager, tasks_requested))
                        self._ready_manager_queue[manager]['free_capacity'] = tasks_requested
                        interesting_managers.add(manager)
                logger.debug("[MAIN] leaving task_outgoing section")

            # If we had received any requests, check if there are tasks that could be passed

            logger.debug("Managers count (total/interesting): {}/{}".format(len(self._ready_manager_queue),
                                                                            len(interesting_managers)))

            if interesting_managers and not self.pending_task_queue.empty():
                shuffled_managers = list(interesting_managers)
                random.shuffle(shuffled_managers)

                while shuffled_managers and not self.pending_task_queue.empty():  # cf. the if statement above...
                    manager = shuffled_managers.pop()
                    tasks_inflight = len(self._ready_manager_queue[manager]['tasks'])
                    real_capacity = min(self._ready_manager_queue[manager]['free_capacity'],
                                        self._ready_manager_queue[manager]['max_capacity'] - tasks_inflight)

                    if (real_capacity and self._ready_manager_queue[manager]['active']):
                        tasks = self.get_tasks(real_capacity)
                        if tasks:
                            self.task_outgoing.send_multipart([manager, b'', pickle.dumps(tasks)])
                            task_count = len(tasks)
                            count += task_count
                            tids = [t['task_id'] for t in tasks]
                            self._ready_manager_queue[manager]['free_capacity'] -= task_count
                            self._ready_manager_queue[manager]['tasks'].extend(tids)
                            logger.debug("[MAIN] Sent tasks: {} to manager {}".format(tids, manager))
                            if self._ready_manager_queue[manager]['free_capacity'] > 0:
                                logger.debug("[MAIN] Manager {} has free_capacity {}".format(manager, self._ready_manager_queue[manager]['free_capacity']))
                                # ... so keep it in the interesting_managers list
                            else:
                                logger.debug("[MAIN] Manager {} is now saturated".format(manager))
                                interesting_managers.remove(manager)
                    else:
                        interesting_managers.remove(manager)
                        # logger.debug("Nothing to send to manager {}".format(manager))
                logger.debug("[MAIN] leaving _ready_manager_queue section, with {} managers still interesting".format(len(interesting_managers)))
            else:
                logger.debug("[MAIN] either no interesting managers or no tasks, so skipping manager pass")
            # Receive any results and forward to client
            if self.results_incoming in self.socks and self.socks[self.results_incoming] == zmq.POLLIN:
                logger.debug("[MAIN] entering results_incoming section")
                manager, *b_messages = self.results_incoming.recv_multipart()
                if manager not in self._ready_manager_queue:
                    logger.warning("[MAIN] Received a result from a un-registered manager: {}".format(manager))
                else:
                    logger.debug("[MAIN] Got {} result items in batch".format(len(b_messages)))
                    for b_message in b_messages:
                        r = pickle.loads(b_message)
                        # logger.debug("[MAIN] Received result for task {} from {}".format(r['task_id'], manager))
                        self._ready_manager_queue[manager]['tasks'].remove(r['task_id'])
                    self.results_outgoing.send_multipart(b_messages)
                    logger.debug("[MAIN] Current tasks: {}".format(self._ready_manager_queue[manager]['tasks']))
                logger.debug("[MAIN] leaving results_incoming section")

            bad_managers = [manager for manager in self._ready_manager_queue if
                            time.time() - self._ready_manager_queue[manager]['last'] > self.heartbeat_threshold]
            for manager in bad_managers:
                logger.debug("[MAIN] Last: {} Current: {}".format(self._ready_manager_queue[manager]['last'], time.time()))
                logger.warning("[MAIN] Too many heartbeats missed for manager {}".format(manager))

                for tid in self._ready_manager_queue[manager]['tasks']:
                    try:
                        raise ManagerLost(manager, self._ready_manager_queue[manager]['hostname'])
                    except Exception:
                        result_package = {'task_id': tid, 'exception': serialize_object(RemoteExceptionWrapper(*sys.exc_info()))}
                        pkl_package = pickle.dumps(result_package)
                        self.results_outgoing.send(pkl_package)
                        logger.warning("[MAIN] Sent failure reports, unregistering manager")
                self._ready_manager_queue.pop(manager, 'None')
                if manager in interesting_managers:
                    interesting_managers.remove(manager)

        delta = time.time() - start
        logger.info("Processed {} tasks in {} seconds".format(count, delta))
        logger.warning("Exiting")