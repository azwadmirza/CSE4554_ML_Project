    def _process_pending_results(self, iterator, one_pass=False):
        '''
        Reads results off the final queue and takes appropriate action
        based on the result (executing callbacks, updating state, etc.).
        '''

        ret_results = []

        def get_original_host(host_name):
            host_name = to_unicode(host_name)
            if host_name in self._inventory._hosts_cache:
                return self._inventory._hosts_cache[host_name]
            else:
                return self._inventory.get_host(host_name)

        def search_handler_blocks(handler_name, handler_blocks):
            for handler_block in handler_blocks:
                for handler_task in handler_block.block:
                    handler_vars = self._variable_manager.get_vars(loader=self._loader, play=iterator._play, task=handler_task)
                    templar = Templar(loader=self._loader, variables=handler_vars)
                    try:
                        # first we check with the full result of get_name(), which may
                        # include the role name (if the handler is from a role). If that
                        # is not found, we resort to the simple name field, which doesn't
                        # have anything extra added to it.
                        target_handler_name = templar.template(handler_task.name)
                        if target_handler_name == handler_name:
                            return handler_task
                        else:
                            target_handler_name = templar.template(handler_task.get_name())
                            if target_handler_name == handler_name:
                                return handler_task
                    except (UndefinedError, AnsibleUndefinedVariable) as e:
                        # We skip this handler due to the fact that it may be using
                        # a variable in the name that was conditionally included via
                        # set_fact or some other method, and we don't want to error
                        # out unnecessarily
                        continue
            return None

        def parent_handler_match(target_handler, handler_name):
            if target_handler:
                if isinstance(target_handler, TaskInclude):
                    try:
                        handler_vars = self._variable_manager.get_vars(loader=self._loader, play=iterator._play, task=target_handler)
                        templar = Templar(loader=self._loader, variables=handler_vars)
                        target_handler_name = templar.template(target_handler.name)
                        if target_handler_name == handler_name:
                            return True
                        else:
                            target_handler_name = templar.template(target_handler.get_name())
                            if target_handler_name == handler_name:
                                return True
                    except (UndefinedError, AnsibleUndefinedVariable) as e:
                        pass
                return parent_handler_match(target_handler._parent, handler_name)
            else:
                return False

        passes = 0
        while not self._tqm._terminated:
            try:
                task_result = self._final_q.get(timeout=0.001)
                original_host = get_original_host(task_result._host)
                original_task = iterator.get_original_task(original_host, task_result._task)
                task_result._host = original_host
                task_result._task = original_task

                # send callbacks for 'non final' results
                if '_ansible_retry' in task_result._result:
                    self._tqm.send_callback('v2_runner_retry', task_result)
                    continue
                elif '_ansible_item_result' in task_result._result:
                    if task_result.is_failed() or task_result.is_unreachable():
                        self._tqm.send_callback('v2_runner_item_on_failed', task_result)
                    elif task_result.is_skipped():
                        self._tqm.send_callback('v2_runner_item_on_skipped', task_result)
                    else:
                        self._tqm.send_callback('v2_runner_item_on_ok', task_result)
                    continue

                if original_task.register:
                    if original_task.run_once:
                        host_list = [host for host in self._inventory.get_hosts(iterator._play.hosts) if host.name not in self._tqm._unreachable_hosts]
                    else:
                        host_list = [original_host]

                    clean_copy = strip_internal_keys(task_result._result)
                    if 'invocation' in clean_copy:
                        del clean_copy['invocation']

                    for target_host in host_list:
                        self._variable_manager.set_nonpersistent_facts(target_host, {original_task.register: clean_copy})

                # all host status messages contain 2 entries: (msg, task_result)
                role_ran = False
                if task_result.is_failed():
                    role_ran = True
                    if not original_task.ignore_errors:
                        display.debug("marking %s as failed" % original_host.name)
                        if original_task.run_once:
                            # if we're using run_once, we have to fail every host here
                            for h in self._inventory.get_hosts(iterator._play.hosts):
                                if h.name not in self._tqm._unreachable_hosts:
                                    state, _ = iterator.get_next_task_for_host(h, peek=True)
                                    iterator.mark_host_failed(h)
                                    state, new_task = iterator.get_next_task_for_host(h, peek=True)
                        else:
                            iterator.mark_host_failed(original_host)

                        # only add the host to the failed list officially if it has
                        # been failed by the iterator
                        if iterator.is_failed(original_host):
                            self._tqm._failed_hosts[original_host.name] = True
                            self._tqm._stats.increment('failures', original_host.name)
                        else:
                            # otherwise, we grab the current state and if we're iterating on
                            # the rescue portion of a block then we save the failed task in a
                            # special var for use within the rescue/always
                            state, _ = iterator.get_next_task_for_host(original_host, peek=True)
                            if state.run_state == iterator.ITERATING_RESCUE:
                                self._variable_manager.set_nonpersistent_facts(
                                    original_host,
                                    dict(
                                        ansible_failed_task=original_task.serialize(),
                                        ansible_failed_result=task_result._result,
                                    ),
                                    )
                    else:
                        self._tqm._stats.increment('ok', original_host.name)
                    self._tqm.send_callback('v2_runner_on_failed', task_result, ignore_errors=original_task.ignore_errors)
                elif task_result.is_unreachable():
                    self._tqm._unreachable_hosts[original_host.name] = True
                    self._tqm._stats.increment('dark', original_host.name)
                    self._tqm.send_callback('v2_runner_on_unreachable', task_result)
                elif task_result.is_skipped():
                    self._tqm._stats.increment('skipped', original_host.name)
                    self._tqm.send_callback('v2_runner_on_skipped', task_result)
                else:
                    role_ran = True

                    if original_task.loop:
                        # this task had a loop, and has more than one result, so
                        # loop over all of them instead of a single result
                        result_items = task_result._result.get('results', [])
                    else:
                        result_items = [ task_result._result ]

                    for result_item in result_items:
                        if '_ansible_notify' in result_item:
                            if task_result.is_changed():
                                # The shared dictionary for notified handlers is a proxy, which
                                # does not detect when sub-objects within the proxy are modified.
                                # So, per the docs, we reassign the list so the proxy picks up and
                                # notifies all other threads
                                for handler_name in result_item['_ansible_notify']:
                                    # Find the handler using the above helper.  First we look up the
                                    # dependency chain of the current task (if it's from a role), otherwise
                                    # we just look through the list of handlers in the current play/all
                                    # roles and use the first one that matches the notify name
                                    if handler_name in self._listening_handlers:
                                        for listening_handler_name in self._listening_handlers[handler_name]:
                                            listening_handler = search_handler_blocks(listening_handler_name, iterator._play.handlers)
                                            if listening_handler is None:
                                                raise AnsibleError("The requested handler listener '%s' was not found in any of the known handlers" % listening_handler_name)
                                            if original_host not in self._notified_handlers[listening_handler]:
                                                self._notified_handlers[listening_handler].append(original_host)
                                                display.vv("NOTIFIED HANDLER %s" % (listening_handler_name,))

                                    else:
                                        target_handler = search_handler_blocks(handler_name, iterator._play.handlers)
                                        if target_handler is not None:
                                            if original_host not in self._notified_handlers[target_handler]:
                                                self._notified_handlers[target_handler].append(original_host)
                                                # FIXME: should this be a callback?
                                                display.vv("NOTIFIED HANDLER %s" % (handler_name,))
                                        else:
                                            # As there may be more than one handler with the notified name as the
                                            # parent, so we just keep track of whether or not we found one at all
                                            found = False
                                            for target_handler in self._notified_handlers:
                                                if parent_handler_match(target_handler, handler_name):
                                                    self._notified_handlers[target_handler].append(original_host)
                                                    display.vv("NOTIFIED HANDLER %s" % (target_handler.get_name(),))
                                                    found = True

                                            # and if none were found, then we raise an error
                                            if not found:
                                                raise AnsibleError("The requested handler '%s' was found in neither the main handlers list nor the listening handlers list" % handler_name)
 

                        if 'add_host' in result_item:
                            # this task added a new host (add_host module)
                            new_host_info = result_item.get('add_host', dict())
                            self._add_host(new_host_info, iterator)

                        elif 'add_group' in result_item:
                            # this task added a new group (group_by module)
                            self._add_group(original_host, result_item)

                        elif 'ansible_facts' in result_item:
                            loop_var = 'item'
                            if original_task.loop_control:
                                loop_var = original_task.loop_control.loop_var or 'item'

                            item = result_item.get(loop_var, None)

                            if original_task.action == 'include_vars':
                                for (var_name, var_value) in iteritems(result_item['ansible_facts']):
                                    # find the host we're actually refering too here, which may
                                    # be a host that is not really in inventory at all
                                    if original_task.delegate_to is not None and original_task.delegate_facts:
                                        task_vars = self._variable_manager.get_vars(loader=self._loader, play=iterator._play, host=host, task=task)
                                        self.add_tqm_variables(task_vars, play=iterator._play)
                                        if item is not None:
                                            task_vars[loop_var] = item
                                        templar = Templar(loader=self._loader, variables=task_vars)
                                        host_name = templar.template(original_task.delegate_to)
                                        actual_host = self._inventory.get_host(host_name)
                                        if actual_host is None:
                                            actual_host = Host(name=host_name)
                                    else:
                                        actual_host = original_host

                                    if original_task.run_once:
                                        host_list = [host for host in self._inventory.get_hosts(iterator._play.hosts) if host.name not in self._tqm._unreachable_hosts]
                                    else:
                                        host_list = [actual_host]

                                    for target_host in host_list:
                                        self._variable_manager.set_host_variable(target_host, var_name, var_value)
                            else:
                                if original_task.run_once:
                                    host_list = [host for host in self._inventory.get_hosts(iterator._play.hosts) if host.name not in self._tqm._unreachable_hosts]
                                else:
                                    host_list = [original_host]

                                for target_host in host_list:
                                    if original_task.action == 'set_fact':
                                        self._variable_manager.set_nonpersistent_facts(target_host, result_item['ansible_facts'].copy())
                                    else:
                                        self._variable_manager.set_host_facts(target_host, result_item['ansible_facts'].copy())

                    if 'diff' in task_result._result:
                        if self._diff:
                            self._tqm.send_callback('v2_on_file_diff', task_result)

                    if original_task.action != 'include':
                        self._tqm._stats.increment('ok', original_host.name)
                        if 'changed' in task_result._result and task_result._result['changed']:
                            self._tqm._stats.increment('changed', original_host.name)

                    # finally, send the ok for this task
                    self._tqm.send_callback('v2_runner_on_ok', task_result)

                self._pending_results -= 1
                if original_host.name in self._blocked_hosts:
                    del self._blocked_hosts[original_host.name]

                # If this is a role task, mark the parent role as being run (if
                # the task was ok or failed, but not skipped or unreachable)
                if original_task._role is not None and role_ran:
                    # lookup the role in the ROLE_CACHE to make sure we're dealing
                    # with the correct object and mark it as executed
                    for (entry, role_obj) in iteritems(iterator._play.ROLE_CACHE[original_task._role._role_name]):
                        if role_obj._uuid == original_task._role._uuid:
                            role_obj._had_task_run[original_host.name] = True

                ret_results.append(task_result)

            except Queue.Empty:
                passes += 1
                if passes > 2:
                   break

            if one_pass:
                break

        return ret_results