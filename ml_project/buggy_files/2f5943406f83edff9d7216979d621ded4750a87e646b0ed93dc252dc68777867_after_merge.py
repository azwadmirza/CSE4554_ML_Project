    def _get_delegated_vars(self, loader, play, task, existing_variables):
        # we unfortunately need to template the delegate_to field here,
        # as we're fetching vars before post_validate has been called on
        # the task that has been passed in
        vars_copy = existing_variables.copy()
        templar = Templar(loader=loader, variables=vars_copy)

        items = []
        if task.loop is not None:
            if task.loop in lookup_loader:
                try:
                    loop_terms = listify_lookup_plugin_terms(terms=task.loop_args, templar=templar, loader=loader, fail_on_undefined=True, convert_bare=False)
                    items = lookup_loader.get(task.loop, loader=loader, templar=templar).run(terms=loop_terms, variables=vars_copy)
                except AnsibleUndefinedVariable as e:
                    # This task will be skipped later due to this, so we just setup
                    # a dummy array for the later code so it doesn't fail
                    items = [None]
            else:
                raise AnsibleError("Unexpected failure in finding the lookup named '%s' in the available lookup plugins" % task.loop)
        else:
            items = [None]

        delegated_host_vars = dict()
        for item in items:
            # update the variables with the item value for templating, in case we need it
            if item is not None:
                vars_copy['item'] = item

            templar.set_available_variables(vars_copy)
            delegated_host_name = templar.template(task.delegate_to, fail_on_undefined=False)
            if not delegated_host_name:
                raise AnsibleError(message="Undefined delegate_to host for task:", obj=task._ds)
            if delegated_host_name in delegated_host_vars:
                # no need to repeat ourselves, as the delegate_to value
                # does not appear to be tied to the loop item variable
                continue

            # a dictionary of variables to use if we have to create a new host below
            # we set the default port based on the default transport here, to make sure
            # we use the proper default for windows
            new_port = C.DEFAULT_REMOTE_PORT
            if C.DEFAULT_TRANSPORT == 'winrm':
                new_port = 5986

            new_delegated_host_vars = dict(
                ansible_host=delegated_host_name,
                ansible_port=new_port,
                ansible_user=C.DEFAULT_REMOTE_USER,
                ansible_connection=C.DEFAULT_TRANSPORT,
            )

            # now try to find the delegated-to host in inventory, or failing that,
            # create a new host on the fly so we can fetch variables for it
            delegated_host = None
            if self._inventory is not None:
                delegated_host = self._inventory.get_host(delegated_host_name)
                # try looking it up based on the address field, and finally
                # fall back to creating a host on the fly to use for the var lookup
                if delegated_host is None:
                    if delegated_host_name in C.LOCALHOST:
                        delegated_host = self._inventory.localhost
                    else:
                        for h in self._inventory.get_hosts(ignore_limits=True, ignore_restrictions=True):
                            # check if the address matches, or if both the delegated_to host
                            # and the current host are in the list of localhost aliases
                            if h.address == delegated_host_name:
                                delegated_host = h
                                break
                        else:
                            delegated_host = Host(name=delegated_host_name)
                            delegated_host.vars.update(new_delegated_host_vars)
            else:
                delegated_host = Host(name=delegated_host_name)
                delegated_host.vars.update(new_delegated_host_vars)

            # now we go fetch the vars for the delegated-to host and save them in our
            # master dictionary of variables to be used later in the TaskExecutor/PlayContext
            delegated_host_vars[delegated_host_name] = self.get_vars(
                loader=loader,
                play=play,
                host=delegated_host,
                task=task,
                include_delegate_to=False,
                include_hostvars=False,
            )

        return delegated_host_vars