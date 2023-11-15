    def _process_pending_results(self, iterator, one_pass=False):
        '''
        Reads results off the final queue and takes appropriate action
        based on the result (executing callbacks, updating state, etc.).
        '''

        ret_results = []

        while not self._final_q.empty() and not self._tqm._terminated:
            try:
                result = self._final_q.get()
                display.debug("got result from result worker: %s" % ([text_type(x) for x in result],))

                # helper method, used to find the original host from the one
                # returned in the result/message, which has been serialized and
                # thus had some information stripped from it to speed up the
                # serialization process
                def get_original_host(host):
                    if host.name in self._inventory._hosts_cache:
                       return self._inventory._hosts_cache[host.name]
                    else:
                       return self._inventory.get_host(host.name)

                # all host status messages contain 2 entries: (msg, task_result)
                if result[0] in ('host_task_ok', 'host_task_failed', 'host_task_skipped', 'host_unreachable'):
                    task_result = result[1]
                    host = get_original_host(task_result._host)
                    task = task_result._task
                    if result[0] == 'host_task_failed' or task_result.is_failed():
                        if not task.ignore_errors:
                            display.debug("marking %s as failed" % host.name)
                            if task.run_once:
                                # if we're using run_once, we have to fail every host here
                                [iterator.mark_host_failed(h) for h in self._inventory.get_hosts(iterator._play.hosts) if h.name not in self._tqm._unreachable_hosts]
                            else:
                                iterator.mark_host_failed(host)

                            # only add the host to the failed list officially if it has
                            # been failed by the iterator
                            if iterator.is_failed(host):
                                self._tqm._failed_hosts[host.name] = True
                                self._tqm._stats.increment('failures', host.name)
                            else:
                                # otherwise, we grab the current state and if we're iterating on
                                # the rescue portion of a block then we save the failed task in a
                                # special var for use within the rescue/always
                                state, _ = iterator.get_next_task_for_host(host, peek=True)
                                if state.run_state == iterator.ITERATING_RESCUE:
                                    original_task = iterator.get_original_task(host, task)
                                    self._variable_manager.set_nonpersistent_facts(
                                        host,
                                        dict(
                                            ansible_failed_task=original_task.serialize(),
                                            ansible_failed_result=task_result._result,
                                        ),
                                    )
                        else:
                            self._tqm._stats.increment('ok', host.name)
                        self._tqm.send_callback('v2_runner_on_failed', task_result, ignore_errors=task.ignore_errors)
                    elif result[0] == 'host_unreachable':
                        self._tqm._unreachable_hosts[host.name] = True
                        self._tqm._stats.increment('dark', host.name)
                        self._tqm.send_callback('v2_runner_on_unreachable', task_result)
                    elif result[0] == 'host_task_skipped':
                        self._tqm._stats.increment('skipped', host.name)
                        self._tqm.send_callback('v2_runner_on_skipped', task_result)
                    elif result[0] == 'host_task_ok':
                        if task.action != 'include':
                            self._tqm._stats.increment('ok', host.name)
                            if 'changed' in task_result._result and task_result._result['changed']:
                                self._tqm._stats.increment('changed', host.name)
                            self._tqm.send_callback('v2_runner_on_ok', task_result)

                        if self._diff:
                            self._tqm.send_callback('v2_on_file_diff', task_result)

                    self._pending_results -= 1
                    if host.name in self._blocked_hosts:
                        del self._blocked_hosts[host.name]

                    # If this is a role task, mark the parent role as being run (if
                    # the task was ok or failed, but not skipped or unreachable)
                    if task_result._task._role is not None and result[0] in ('host_task_ok', 'host_task_failed'):
                        # lookup the role in the ROLE_CACHE to make sure we're dealing
                        # with the correct object and mark it as executed
                        for (entry, role_obj) in iteritems(iterator._play.ROLE_CACHE[task_result._task._role._role_name]):
                            if role_obj._uuid == task_result._task._role._uuid:
                                role_obj._had_task_run[host.name] = True

                    ret_results.append(task_result)

                elif result[0] == 'add_host':
                    result_item = result[1]
                    new_host_info = result_item.get('add_host', dict())

                    self._add_host(new_host_info, iterator)

                elif result[0] == 'add_group':
                    host = get_original_host(result[1])
                    result_item = result[2]
                    self._add_group(host, result_item)

                elif result[0] == 'notify_handler':
                    task_result  = result[1]
                    handler_name = result[2]

                    original_host = get_original_host(task_result._host)
                    original_task = iterator.get_original_task(original_host, task_result._task)

                    def search_handler_blocks(handler_blocks):
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
                                except (UndefinedError, AnsibleUndefinedVariable):
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
                            return parent_handler_match(target_handler._task_include, handler_name)
                        else:
                            return False

                    # Find the handler using the above helper.  First we look up the
                    # dependency chain of the current task (if it's from a role), otherwise
                    # we just look through the list of handlers in the current play/all
                    # roles and use the first one that matches the notify name
                    target_handler = search_handler_blocks(iterator._play.handlers)
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
                            raise AnsibleError("The requested handler '%s' was not found in the main handlers list" % handler_name)

                elif result[0] == 'register_host_var':
                    # essentially the same as 'set_host_var' below, however we
                    # never follow the delegate_to value for registered vars and
                    # the variable goes in the fact_cache
                    host      = get_original_host(result[1])
                    task      = result[2]
                    var_value = wrap_var(result[3])
                    var_name  = task.register

                    if task.run_once:
                        host_list = [host for host in self._inventory.get_hosts(iterator._play.hosts) if host.name not in self._tqm._unreachable_hosts]
                    else:
                        host_list = [host]

                    for target_host in host_list:
                        self._variable_manager.set_nonpersistent_facts(target_host, {var_name: var_value})

                elif result[0] in ('set_host_var', 'set_host_facts'):
                    host = get_original_host(result[1])
                    task = result[2]
                    item = result[3]

                    # find the host we're actually refering too here, which may
                    # be a host that is not really in inventory at all
                    if task.delegate_to is not None and task.delegate_facts:
                        task_vars = self._variable_manager.get_vars(loader=self._loader, play=iterator._play, host=host, task=task)
                        self.add_tqm_variables(task_vars, play=iterator._play)
                        loop_var = 'item'
                        if task.loop_control:
                            loop_var = task.loop_control.loop_var or 'item'
                        if item is not None:
                            task_vars[loop_var] = item
                        templar = Templar(loader=self._loader, variables=task_vars)
                        host_name = templar.template(task.delegate_to)
                        actual_host = self._inventory.get_host(host_name)
                        if actual_host is None:
                            actual_host = Host(name=host_name)
                    else:
                        actual_host = host

                    if task.run_once:
                        host_list = [host for host in self._inventory.get_hosts(iterator._play.hosts) if host.name not in self._tqm._unreachable_hosts]
                    else:
                        host_list = [actual_host]

                    if result[0] == 'set_host_var':
                        var_name  = result[4]
                        var_value = result[5]
                        for target_host in host_list:
                            self._variable_manager.set_host_variable(target_host, var_name, var_value)
                    elif result[0] == 'set_host_facts':
                        facts = result[4]
                        for target_host in host_list:
                            if task.action == 'set_fact':
                                self._variable_manager.set_nonpersistent_facts(target_host, facts.copy())
                            else:
                                self._variable_manager.set_host_facts(target_host, facts.copy())
                elif result[0].startswith('v2_runner_item') or result[0] == 'v2_runner_retry':
                    self._tqm.send_callback(result[0], result[1])
                elif result[0] == 'v2_on_file_diff':
                    if self._diff:
                        self._tqm.send_callback('v2_on_file_diff', result[1])
                else:
                    raise AnsibleError("unknown result message received: %s" % result[0])

            except Queue.Empty:
                time.sleep(0.0001)

            if one_pass:
                break

        return ret_results