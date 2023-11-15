    def _execute_meta(self, task, play_context, iterator, target_host):

        # meta tasks store their args in the _raw_params field of args,
        # since they do not use k=v pairs, so get that
        meta_action = task.args.get('_raw_params')

        # FIXME(s):
        # * raise an error or show a warning when a conditional is used
        #   on a meta task that doesn't support them

        def _evaluate_conditional(h):
            all_vars = self._variable_manager.get_vars(loader=self._loader, play=iterator._play, host=h, task=task)
            templar = Templar(loader=self._loader, variables=all_vars)
            return task.evaluate_conditional(templar, all_vars)

        skipped = False
        msg = ''
        if meta_action == 'noop':
            # FIXME: issue a callback for the noop here?
            msg="noop"
        elif meta_action == 'flush_handlers':
            self.run_handlers(iterator, play_context)
            msg = "ran handlers"
        elif meta_action == 'refresh_inventory':
            self._inventory.refresh_inventory()
            msg = "inventory successfully refreshed"
        elif meta_action == 'clear_facts':
            if _evaluate_conditional(target_host):
                for host in self._inventory.get_hosts(iterator._play.hosts):
                    self._variable_manager.clear_facts(host)
                msg = "facts cleared"
            else:
                skipped = True
        elif meta_action == 'clear_host_errors':
            if _evaluate_conditional(target_host):
                for host in self._inventory.get_hosts(iterator._play.hosts):
                    self._tqm._failed_hosts.pop(host.name, False)
                    self._tqm._unreachable_hosts.pop(host.name, False)
                    iterator._host_states[host.name].fail_state = iterator.FAILED_NONE
                msg="cleared host errors"
            else:
                skipped = True
        elif meta_action == 'end_play':
            if _evaluate_conditional(target_host):
                for host in self._inventory.get_hosts(iterator._play.hosts):
                    if not host.name in self._tqm._unreachable_hosts:
                        iterator._host_states[host.name].run_state = iterator.ITERATING_COMPLETE
                msg="ending play"
        elif meta_action == 'reset_connection':
            connection = connection_loader.get(play_context.connection, play_context, '/dev/null')
            connection.reset()
            msg= 'reset connection'
        else:
            raise AnsibleError("invalid meta action requested: %s" % meta_action, obj=task._ds)

        result = { 'msg': msg }
        if skipped:
            result['skipped'] = True
        else:
            result['changed'] = False

        display.vv("META: %s" % msg)

        return [TaskResult(target_host, task, result)]