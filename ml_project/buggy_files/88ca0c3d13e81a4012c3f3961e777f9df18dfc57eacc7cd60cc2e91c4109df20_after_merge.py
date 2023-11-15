    def _execute(self, variables=None):
        '''
        The primary workhorse of the executor system, this runs the task
        on the specified host (which may be the delegated_to host) and handles
        the retry/until and block rescue/always execution
        '''

        if variables is None:
            variables = self._job_vars

        templar = Templar(loader=self._loader, shared_loader_obj=self._shared_loader_obj, variables=variables)

        context_validation_error = None
        try:
            # apply the given task's information to the connection info,
            # which may override some fields already set by the play or
            # the options specified on the command line
            self._play_context = self._play_context.set_task_and_variable_override(task=self._task, variables=variables, templar=templar)

            # fields set from the play/task may be based on variables, so we have to
            # do the same kind of post validation step on it here before we use it.
            self._play_context.post_validate(templar=templar)

            # now that the play context is finalized, if the remote_addr is not set
            # default to using the host's address field as the remote address
            if not self._play_context.remote_addr:
                self._play_context.remote_addr = self._host.address

            # We also add "magic" variables back into the variables dict to make sure
            # a certain subset of variables exist.
            self._play_context.update_vars(variables)

            # FIXME: update connection/shell plugin options
        except AnsibleError as e:
            # save the error, which we'll raise later if we don't end up
            # skipping this task during the conditional evaluation step
            context_validation_error = e

        # Evaluate the conditional (if any) for this task, which we do before running
        # the final task post-validation. We do this before the post validation due to
        # the fact that the conditional may specify that the task be skipped due to a
        # variable not being present which would otherwise cause validation to fail
        try:
            if not self._task.evaluate_conditional(templar, variables):
                display.debug("when evaluation is False, skipping this task")
                return dict(changed=False, skipped=True, skip_reason='Conditional result was False', _ansible_no_log=self._play_context.no_log)
        except AnsibleError as e:
            # loop error takes precedence
            if self._loop_eval_error is not None:
                # Display the error from the conditional as well to prevent
                # losing information useful for debugging.
                display.v(to_text(e))
                raise self._loop_eval_error  # pylint: disable=raising-bad-type
            raise

        # Not skipping, if we had loop error raised earlier we need to raise it now to halt the execution of this task
        if self._loop_eval_error is not None:
            raise self._loop_eval_error  # pylint: disable=raising-bad-type

        # if we ran into an error while setting up the PlayContext, raise it now
        if context_validation_error is not None:
            raise context_validation_error  # pylint: disable=raising-bad-type

        # if this task is a TaskInclude, we just return now with a success code so the
        # main thread can expand the task list for the given host
        if self._task.action in ('include', 'include_tasks'):
            include_args = self._task.args.copy()
            include_file = include_args.pop('_raw_params', None)
            if not include_file:
                return dict(failed=True, msg="No include file was specified to the include")

            include_file = templar.template(include_file)
            return dict(include=include_file, include_args=include_args)

        # if this task is a IncludeRole, we just return now with a success code so the main thread can expand the task list for the given host
        elif self._task.action == 'include_role':
            include_args = self._task.args.copy()
            return dict(include_args=include_args)

        # Now we do final validation on the task, which sets all fields to their final values.
        try:
            self._task.post_validate(templar=templar)
        except AnsibleError:
            raise
        except Exception:
            return dict(changed=False, failed=True, _ansible_no_log=self._play_context.no_log, exception=to_text(traceback.format_exc()))
        if '_variable_params' in self._task.args:
            variable_params = self._task.args.pop('_variable_params')
            if isinstance(variable_params, dict):
                if C.INJECT_FACTS_AS_VARS:
                    display.warning("Using a variable for a task's 'args' is unsafe in some situations "
                                    "(see https://docs.ansible.com/ansible/devel/reference_appendices/faq.html#argsplat-unsafe)")
                variable_params.update(self._task.args)
                self._task.args = variable_params

        # get the connection and the handler for this execution
        if (not self._connection or
                not getattr(self._connection, 'connected', False) or
                self._play_context.remote_addr != self._connection._play_context.remote_addr):
            self._connection = self._get_connection(variables=variables, templar=templar)
        else:
            # if connection is reused, its _play_context is no longer valid and needs
            # to be replaced with the one templated above, in case other data changed
            self._connection._play_context = self._play_context

        if self._task.delegate_to:
            # use vars from delegated host (which already include task vars) instead of original host
            delegated_vars = variables.get('ansible_delegated_vars', {}).get(self._task.delegate_to, {})
            orig_vars = templar.available_variables
            templar.available_variables = delegated_vars
            plugin_vars = self._set_connection_options(delegated_vars, templar)
            templar.available_variables = orig_vars
        else:
            # just use normal host vars
            plugin_vars = self._set_connection_options(variables, templar)

        # get handler
        self._handler = self._get_action_handler(connection=self._connection, templar=templar)

        # Apply default params for action/module, if present
        self._task.args = get_action_args_with_defaults(
            self._task.action, self._task.args, self._task.module_defaults, templar, self._task._ansible_internal_redirect_list
        )

        # And filter out any fields which were set to default(omit), and got the omit token value
        omit_token = variables.get('omit')
        if omit_token is not None:
            self._task.args = remove_omit(self._task.args, omit_token)

        # Read some values from the task, so that we can modify them if need be
        if self._task.until:
            retries = self._task.retries
            if retries is None:
                retries = 3
            elif retries <= 0:
                retries = 1
            else:
                retries += 1
        else:
            retries = 1

        delay = self._task.delay
        if delay < 0:
            delay = 1

        # make a copy of the job vars here, in case we need to update them
        # with the registered variable value later on when testing conditions
        vars_copy = variables.copy()

        display.debug("starting attempt loop")
        result = None
        for attempt in xrange(1, retries + 1):
            display.debug("running the handler")
            try:
                if self._task.timeout:
                    old_sig = signal.signal(signal.SIGALRM, task_timeout)
                    signal.alarm(self._task.timeout)
                result = self._handler.run(task_vars=variables)
            except AnsibleActionSkip as e:
                return dict(skipped=True, msg=to_text(e))
            except AnsibleActionFail as e:
                return dict(failed=True, msg=to_text(e))
            except AnsibleConnectionFailure as e:
                return dict(unreachable=True, msg=to_text(e))
            except TaskTimeoutError as e:
                msg = 'The %s action failed to execute in the expected time frame (%d) and was terminated' % (self._task.action, self._task.timeout)
                return dict(failed=True, msg=msg)
            finally:
                if self._task.timeout:
                    signal.alarm(0)
                    old_sig = signal.signal(signal.SIGALRM, old_sig)
                self._handler.cleanup()
            display.debug("handler run complete")

            # preserve no log
            result["_ansible_no_log"] = self._play_context.no_log

            # update the local copy of vars with the registered value, if specified,
            # or any facts which may have been generated by the module execution
            if self._task.register:
                if not isidentifier(self._task.register):
                    raise AnsibleError("Invalid variable name in 'register' specified: '%s'" % self._task.register)

                vars_copy[self._task.register] = result = wrap_var(result)

            if self._task.async_val > 0:
                if self._task.poll > 0 and not result.get('skipped') and not result.get('failed'):
                    result = self._poll_async_result(result=result, templar=templar, task_vars=vars_copy)
                    # FIXME callback 'v2_runner_on_async_poll' here

                # ensure no log is preserved
                result["_ansible_no_log"] = self._play_context.no_log

            # helper methods for use below in evaluating changed/failed_when
            def _evaluate_changed_when_result(result):
                if self._task.changed_when is not None and self._task.changed_when:
                    cond = Conditional(loader=self._loader)
                    cond.when = self._task.changed_when
                    result['changed'] = cond.evaluate_conditional(templar, vars_copy)

            def _evaluate_failed_when_result(result):
                if self._task.failed_when:
                    cond = Conditional(loader=self._loader)
                    cond.when = self._task.failed_when
                    failed_when_result = cond.evaluate_conditional(templar, vars_copy)
                    result['failed_when_result'] = result['failed'] = failed_when_result
                else:
                    failed_when_result = False
                return failed_when_result

            if 'ansible_facts' in result:
                if self._task.action in ('set_fact', 'include_vars'):
                    vars_copy.update(result['ansible_facts'])
                else:
                    # TODO: cleaning of facts should eventually become part of taskresults instead of vars
                    af = wrap_var(result['ansible_facts'])
                    vars_copy.update(namespace_facts(af))
                    if C.INJECT_FACTS_AS_VARS:
                        vars_copy.update(clean_facts(af))

            # set the failed property if it was missing.
            if 'failed' not in result:
                # rc is here for backwards compatibility and modules that use it instead of 'failed'
                if 'rc' in result and result['rc'] not in [0, "0"]:
                    result['failed'] = True
                else:
                    result['failed'] = False

            # Make attempts and retries available early to allow their use in changed/failed_when
            if self._task.until:
                result['attempts'] = attempt

            # set the changed property if it was missing.
            if 'changed' not in result:
                result['changed'] = False

            # re-update the local copy of vars with the registered value, if specified,
            # or any facts which may have been generated by the module execution
            # This gives changed/failed_when access to additional recently modified
            # attributes of result
            if self._task.register:
                vars_copy[self._task.register] = result = wrap_var(result)

            # if we didn't skip this task, use the helpers to evaluate the changed/
            # failed_when properties
            if 'skipped' not in result:
                _evaluate_changed_when_result(result)
                _evaluate_failed_when_result(result)

            if retries > 1:
                cond = Conditional(loader=self._loader)
                cond.when = self._task.until
                if cond.evaluate_conditional(templar, vars_copy):
                    break
                else:
                    # no conditional check, or it failed, so sleep for the specified time
                    if attempt < retries:
                        result['_ansible_retry'] = True
                        result['retries'] = retries
                        display.debug('Retrying task, attempt %d of %d' % (attempt, retries))
                        self._final_q.put(TaskResult(self._host.name, self._task._uuid, result, task_fields=self._task.dump_attrs()), block=False)
                        time.sleep(delay)
                        self._handler = self._get_action_handler(connection=self._connection, templar=templar)
        else:
            if retries > 1:
                # we ran out of attempts, so mark the result as failed
                result['attempts'] = retries - 1
                result['failed'] = True

        # do the final update of the local variables here, for both registered
        # values and any facts which may have been created
        if self._task.register:
            variables[self._task.register] = result = wrap_var(result)

        if 'ansible_facts' in result:
            if self._task.action in ('set_fact', 'include_vars'):
                variables.update(result['ansible_facts'])
            else:
                # TODO: cleaning of facts should eventually become part of taskresults instead of vars
                af = wrap_var(result['ansible_facts'])
                variables.update(namespace_facts(af))
                if C.INJECT_FACTS_AS_VARS:
                    variables.update(clean_facts(af))

        # save the notification target in the result, if it was specified, as
        # this task may be running in a loop in which case the notification
        # may be item-specific, ie. "notify: service {{item}}"
        if self._task.notify is not None:
            result['_ansible_notify'] = self._task.notify

        # add the delegated vars to the result, so we can reference them
        # on the results side without having to do any further templating
        if self._task.delegate_to:
            result["_ansible_delegated_vars"] = {'ansible_delegated_host': self._task.delegate_to}
            for k in plugin_vars:
                result["_ansible_delegated_vars"][k] = delegated_vars.get(k)
        # and return
        display.debug("attempt loop complete, returning result")
        return result