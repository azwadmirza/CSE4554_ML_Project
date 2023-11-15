    def save_task_result(self, idents, msg):
        """save the result of a completed task."""
        client_id = idents[0]
        try:
            msg = self.session.unserialize(msg)
        except Exception:
            self.log.error("task::invalid task result message send to %r: %r",
                    client_id, msg, exc_info=True)
            return

        parent = msg['parent_header']
        if not parent:
            # print msg
            self.log.warn("Task %r had no parent!", msg)
            return
        msg_id = parent['msg_id']
        if msg_id in self.unassigned:
            self.unassigned.remove(msg_id)

        header = msg['header']
        engine_uuid = header.get('engine', None)
        eid = self.by_ident.get(engine_uuid, None)
        
        status = header.get('status', None)

        if msg_id in self.pending:
            self.log.info("task::task %r finished on %s", msg_id, eid)
            self.pending.remove(msg_id)
            self.all_completed.add(msg_id)
            if eid is not None:
                if status != 'aborted':
                    self.completed[eid].append(msg_id)
                if msg_id in self.tasks[eid]:
                    self.tasks[eid].remove(msg_id)
            completed = header['date']
            started = header.get('started', None)
            result = {
                'result_header' : header,
                'result_content': msg['content'],
                'started' : started,
                'completed' : completed,
                'received' : datetime.now(),
                'engine_uuid': engine_uuid,
            }

            result['result_buffers'] = msg['buffers']
            try:
                self.db.update_record(msg_id, result)
            except Exception:
                self.log.error("DB Error saving task request %r", msg_id, exc_info=True)

        else:
            self.log.debug("task::unknown task %r finished", msg_id)