    def start(self, priority_queue, node_queue, resource_queue) -> None:

        self._kill_event = threading.Event()
        self._priority_queue_pull_thread = threading.Thread(target=self._migrate_logs_to_internal,
                                                            args=(
                                                                priority_queue, 'priority', self._kill_event,),
                                                            name="Monitoring-migrate-priority",
                                                            daemon=True,
                                                            )
        self._priority_queue_pull_thread.start()

        self._node_queue_pull_thread = threading.Thread(target=self._migrate_logs_to_internal,
                                                        args=(
                                                            node_queue, 'node', self._kill_event,),
                                                        name="Monitoring-migrate-node",
                                                        daemon=True,
                                                        )
        self._node_queue_pull_thread.start()

        self._resource_queue_pull_thread = threading.Thread(target=self._migrate_logs_to_internal,
                                                            args=(
                                                                resource_queue, 'resource', self._kill_event,),
                                                            name="Monitoring-migrate-resource",
                                                            daemon=True,
                                                            )
        self._resource_queue_pull_thread.start()

        """
        maintain a set to track the tasks that are already INSERTed into database
        to prevent race condition that the first resource message (indicate 'running' state)
        arrives before the first task message. In such a case, the resource table
        primary key would be violated.
        If that happens, the message will be added to deferred_resource_messages and processed later.

        """
        inserted_tasks = set()  # type: Set[object]

        """
        like inserted_tasks but for task,try tuples
        """
        inserted_tries = set()  # type: Set[Any]

        # for any task ID, we can defer exactly one message, which is the
        # assumed-to-be-unique first message (with first message flag set).
        # The code prior to this patch will discard previous message in
        # the case of multiple messages to defer.
        deferred_resource_messages = {}  # type: Dict[str, Any]

        while (not self._kill_event.is_set() or
               self.pending_priority_queue.qsize() != 0 or self.pending_resource_queue.qsize() != 0 or
               priority_queue.qsize() != 0 or resource_queue.qsize() != 0):

            """
            WORKFLOW_INFO and TASK_INFO messages (i.e. priority messages)

            """
            logger.debug("""Checking STOP conditions: {}, {}, {}, {}, {}""".format(
                              self._kill_event.is_set(),
                              self.pending_priority_queue.qsize() != 0, self.pending_resource_queue.qsize() != 0,
                              priority_queue.qsize() != 0, resource_queue.qsize() != 0))

            # This is the list of resource messages which can be reprocessed as if they
            # had just arrived because the corresponding first task message has been
            # processed (corresponding by task id)
            reprocessable_first_resource_messages = []

            # Get a batch of priority messages
            priority_messages = self._get_messages_in_batch(self.pending_priority_queue,
                                                            interval=self.batching_interval,
                                                            threshold=self.batching_threshold)
            if priority_messages:
                logger.debug(
                    "Got {} messages from priority queue".format(len(priority_messages)))
                task_info_update_messages, task_info_insert_messages, task_info_all_messages = [], [], []
                try_update_messages, try_insert_messages, try_all_messages = [], [], []
                for msg_type, msg in priority_messages:
                    if msg_type.value == MessageType.WORKFLOW_INFO.value:
                        if "python_version" in msg:   # workflow start message
                            logger.debug(
                                "Inserting workflow start info to WORKFLOW table")
                            self._insert(table=WORKFLOW, messages=[msg])
                            self.workflow_start_message = msg
                        else:                         # workflow end message
                            logger.debug(
                                "Updating workflow end info to WORKFLOW table")
                            self._update(table=WORKFLOW,
                                         columns=['run_id', 'tasks_failed_count',
                                                  'tasks_completed_count', 'time_completed'],
                                         messages=[msg])
                            self.workflow_end = True

                    elif msg_type.value == MessageType.TASK_INFO.value:
                        task_try_id = str(msg['task_id']) + "." + str(msg['try_id'])
                        task_info_all_messages.append(msg)
                        if msg['task_id'] in inserted_tasks:
                            task_info_update_messages.append(msg)
                        else:
                            inserted_tasks.add(msg['task_id'])
                            task_info_insert_messages.append(msg)

                        try_all_messages.append(msg)
                        if task_try_id in inserted_tries:
                            try_update_messages.append(msg)
                        else:
                            inserted_tries.add(task_try_id)
                            try_insert_messages.append(msg)

                            # check if there is a left_message for this task
                            if task_try_id in deferred_resource_messages:
                                reprocessable_first_resource_messages.append(
                                    deferred_resource_messages.pop(task_try_id))
                    else:
                        raise RuntimeError("Unexpected message type {} received on priority queue".format(msg_type))

                logger.debug("Updating and inserting TASK_INFO to all tables")
                logger.debug("Updating {} TASK_INFO into workflow table".format(len(task_info_update_messages)))
                self._update(table=WORKFLOW,
                             columns=['run_id', 'tasks_failed_count',
                                      'tasks_completed_count'],
                             messages=task_info_all_messages)

                if task_info_insert_messages:
                    self._insert(table=TASK, messages=task_info_insert_messages)
                    logger.debug(
                        "There are {} inserted task records".format(len(inserted_tasks)))

                if task_info_update_messages:
                    logger.debug("Updating {} TASK_INFO into task table".format(len(task_info_update_messages)))
                    self._update(table=TASK,
                                 columns=['task_time_invoked',
                                          'task_time_returned',
                                          'run_id', 'task_id',
                                          'task_fail_count',
                                          'task_hashsum'],
                                 messages=task_info_update_messages)
                logger.debug("Inserting {} task_info_all_messages into status table".format(len(task_info_all_messages)))

                self._insert(table=STATUS, messages=task_info_all_messages)

                if try_insert_messages:
                    logger.debug("Inserting {} TASK_INFO to try table".format(len(try_insert_messages)))
                    self._insert(table=TRY, messages=try_insert_messages)
                    logger.debug(
                        "There are {} inserted task records".format(len(inserted_tasks)))

                if try_update_messages:
                    logger.debug("Updating {} TASK_INFO into try table".format(len(try_update_messages)))
                    self._update(table=TRY,
                                 columns=['run_id', 'task_id', 'try_id',
                                          'task_fail_history',
                                          'task_try_time_launched',
                                          'task_try_time_returned'],
                                 messages=try_update_messages)

            """
            NODE_INFO messages

            """
            node_info_messages = self._get_messages_in_batch(self.pending_node_queue,
                                                             interval=self.batching_interval,
                                                             threshold=self.batching_threshold)
            if node_info_messages:
                logger.debug(
                    "Got {} messages from node queue".format(len(node_info_messages)))
                self._insert(table=NODE, messages=node_info_messages)

            """
            Resource info messages

            """
            resource_messages = self._get_messages_in_batch(self.pending_resource_queue,
                                                            interval=self.batching_interval,
                                                            threshold=self.batching_threshold)

            if resource_messages:
                logger.debug(
                    "Got {} messages from resource queue, {} reprocessable".format(len(resource_messages), len(reprocessable_first_resource_messages)))

                insert_resource_messages = []
                for msg in resource_messages:
                    task_try_id = str(msg['task_id']) + "." + str(msg['try_id'])
                    if msg['first_msg']:
                        # Update the running time to try table if first message
                        msg['task_status_name'] = States.running.name
                        msg['task_try_time_running'] = msg['timestamp']

                        if task_try_id in inserted_tries:  # TODO: needs to become task_id and try_id, and check against inserted_tries
                            reprocessable_first_resource_messages.append(msg)
                        else:
                            if task_try_id in deferred_resource_messages:
                                logger.error("Task {} already has a deferred resource message. Discarding previous message.".format(msg['task_id']))
                            deferred_resource_messages[task_try_id] = msg
                    else:
                        # Insert to resource table if not first message
                        insert_resource_messages.append(msg)

                if insert_resource_messages:
                    self._insert(table=RESOURCE, messages=insert_resource_messages)

            if reprocessable_first_resource_messages:
                self._insert(table=STATUS, messages=reprocessable_first_resource_messages)
                self._update(table=TRY,
                             columns=['task_try_time_running',
                                      'run_id', 'task_id', 'try_id',
                                      'hostname'],
                             messages=reprocessable_first_resource_messages)