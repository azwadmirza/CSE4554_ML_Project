    def allocate_top_resources(self, fetch_requests=False):
        """
        Allocate resources given the order in AssignerActor
        """
        t = time.time()
        if self._worker_metrics is None or self._worker_metric_time + 1 < time.time():
            # update worker metrics from ResourceActor
            self._worker_metrics = self._resource_ref.get_workers_meta()
            self._worker_metric_time = t
        if not self._worker_metrics:
            return

        if fetch_requests:
            requests = self._assigner_ref.get_allocate_requests()
            if not requests:
                return
            max_allocates = sys.maxsize if any(v is None for v in requests) else sum(requests)
        else:
            max_allocates = sys.maxsize

        unassigned = []
        reject_workers = set()
        assigned = 0
        # the assigning procedure will continue till all workers rejected
        # or max_allocates reached
        while len(reject_workers) < len(self._worker_metrics) and assigned < max_allocates:
            item = self._assigner_ref.pop_head()
            if not item:
                break

            try:
                alloc_ep, rejects = self._allocate_resource(
                    item.session_id, item.op_key, item.op_info, item.target_worker,
                    reject_workers=reject_workers)
            except:  # noqa: E722
                logger.exception('Unexpected error occurred in %s', self.uid)
                if item.callback:  # pragma: no branch
                    self.tell_promise(item.callback, *sys.exc_info(), _accept=False)
                else:
                    self.get_actor_ref(BaseOperandActor.gen_uid(item.session_id, item.op_key)) \
                        .handle_unexpected_failure(*sys.exc_info(), _tell=True, _wait=False)
                continue

            # collect workers failed to assign operand to
            reject_workers.update(rejects)
            if alloc_ep:
                # assign successfully, we remove the application
                self._assigner_ref.remove_apply(item.op_key, _tell=True)
                self._session_last_assigns[item.session_id] = time.time()
                assigned += 1
            else:
                # put the unassigned item into unassigned list to add back to the queue later
                unassigned.append(item)
        if unassigned:
            # put unassigned back to the queue, if any
            self._assigner_ref.extend(unassigned, _tell=True)

        if not fetch_requests:
            self._assigner_ref.get_allocate_requests(_tell=True, _wait=False)