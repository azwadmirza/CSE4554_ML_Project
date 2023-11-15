    def get_vars(self, loader, play=None, host=None, task=None, include_hostvars=True, include_delegate_to=True, use_cache=True):
        '''
        Returns the variables, with optional "context" given via the parameters
        for the play, host, and task (which could possibly result in different
        sets of variables being returned due to the additional context).

        The order of precedence is:
        - play->roles->get_default_vars (if there is a play context)
        - group_vars_files[host] (if there is a host context)
        - host_vars_files[host] (if there is a host context)
        - host->get_vars (if there is a host context)
        - fact_cache[host] (if there is a host context)
        - play vars (if there is a play context)
        - play vars_files (if there's no host context, ignore
          file names that cannot be templated)
        - task->get_vars (if there is a task context)
        - vars_cache[host] (if there is a host context)
        - extra vars
        '''

        display.debug("in VariableManager get_vars()")
        cache_entry = self._get_cache_entry(play=play, host=host, task=task)
        if cache_entry in VARIABLE_CACHE and use_cache:
            display.debug("vars are cached, returning them now")
            return VARIABLE_CACHE[cache_entry]

        all_vars = dict()
        magic_variables = self._get_magic_variables(
            loader=loader,
            play=play,
            host=host,
            task=task,
            include_hostvars=include_hostvars,
            include_delegate_to=include_delegate_to,
        )

        if play:
            # first we compile any vars specified in defaults/main.yml
            # for all roles within the specified play
            for role in play.get_roles():
                all_vars = combine_vars(all_vars, role.get_default_vars())

            # if we have a task in this context, and that task has a role, make
            # sure it sees its defaults above any other roles, as we previously
            # (v1) made sure each task had a copy of its roles default vars
            if task and task._role is not None:
                dep_chain = []
                if task._block:
                    dep_chain = task._block.get_dep_chain()
                all_vars = combine_vars(all_vars, task._role.get_default_vars(dep_chain=dep_chain))

        if host:
            # next, if a host is specified, we load any vars from group_vars
            # files and then any vars from host_vars files which may apply to
            # this host or the groups it belongs to

            # we merge in the special 'all' group_vars first, if they exist
            if 'all' in self._group_vars_files:
                data = preprocess_vars(self._group_vars_files['all'])
                for item in data:
                    all_vars = combine_vars(all_vars, item)

            # we merge in vars from groups specified in the inventory (INI or script)
            all_vars = combine_vars(all_vars, host.get_group_vars())

            for group in sorted(host.get_groups(), key=lambda g: g.depth):
                if group.name in self._group_vars_files and group.name != 'all':
                    for data in self._group_vars_files[group.name]:
                        data = preprocess_vars(data)
                        for item in data:
                            all_vars = combine_vars(all_vars, item)

            # then we merge in vars from the host specified in the inventory (INI or script)
            all_vars = combine_vars(all_vars, host.get_vars())

            # then we merge in the host_vars/<hostname> file, if it exists
            host_name = host.get_name()
            if host_name in self._host_vars_files:
                for data in self._host_vars_files[host_name]:
                    data = preprocess_vars(data)
                    for item in data:
                        all_vars = combine_vars(all_vars, item)

            # finally, the facts caches for this host, if it exists
            try:
                host_facts = wrap_var(self._fact_cache.get(host.name, dict()))
                all_vars = combine_vars(all_vars, host_facts)
            except KeyError:
                pass

        if play:
            all_vars = combine_vars(all_vars, play.get_vars())

            for vars_file_item in play.get_vars_files():
                # create a set of temporary vars here, which incorporate the extra
                # and magic vars so we can properly template the vars_files entries
                temp_vars = combine_vars(all_vars, self._extra_vars)
                temp_vars = combine_vars(temp_vars, magic_variables)
                templar = Templar(loader=loader, variables=temp_vars)

                # we assume each item in the list is itself a list, as we
                # support "conditional includes" for vars_files, which mimics
                # the with_first_found mechanism.
                vars_file_list = vars_file_item
                if not isinstance(vars_file_list, list):
                     vars_file_list = [ vars_file_list ]

                # now we iterate through the (potential) files, and break out
                # as soon as we read one from the list. If none are found, we
                # raise an error, which is silently ignored at this point.
                try:
                    for vars_file in vars_file_list:
                        vars_file = templar.template(vars_file)
                        try:
                            data = preprocess_vars(loader.load_from_file(vars_file))
                            if data is not None:
                                for item in data:
                                    all_vars = combine_vars(all_vars, item)
                            break
                        except AnsibleFileNotFound as e:
                            # we continue on loader failures
                            continue
                        except AnsibleParserError as e:
                            raise
                    else:
                        raise AnsibleFileNotFound("vars file %s was not found" % vars_file_item)
                except (UndefinedError, AnsibleUndefinedVariable):
                    if host is not None and self._fact_cache.get(host.name, dict()).get('module_setup') and task is not None:
                        raise AnsibleUndefinedVariable("an undefined variable was found when attempting to template the vars_files item '%s'" % vars_file_item, obj=vars_file_item)
                    else:
                        # we do not have a full context here, and the missing variable could be
                        # because of that, so just show a warning and continue
                        display.vvv("skipping vars_file '%s' due to an undefined variable" % vars_file_item)
                        continue

            # By default, we now merge in all vars from all roles in the play,
            # unless the user has disabled this via a config option
            if not C.DEFAULT_PRIVATE_ROLE_VARS:
                for role in play.get_roles():
                    all_vars = combine_vars(all_vars, role.get_vars(include_params=False))

        # next, we merge in the vars from the role, which will specifically
        # follow the role dependency chain, and then we merge in the tasks
        # vars (which will look at parent blocks/task includes)
        if task:
            if task._role:
                dep_chain = []
                if task._block:
                    dep_chain = task._block.get_dep_chain()
                all_vars = combine_vars(all_vars, task._role.get_vars(dep_chain=dep_chain, include_params=False))
            all_vars = combine_vars(all_vars, task.get_vars())

        # next, we merge in the vars cache (include vars) and nonpersistent
        # facts cache (set_fact/register), in that order
        if host:
            all_vars = combine_vars(all_vars, self._vars_cache.get(host.get_name(), dict()))
            all_vars = combine_vars(all_vars, self._nonpersistent_fact_cache.get(host.name, dict()))

        # next, we merge in role params and task include params
        if task:
            if task._role:
                dep_chain = []
                if task._block:
                    dep_chain = task._block.get_dep_chain()
                all_vars = combine_vars(all_vars, task._role.get_role_params(dep_chain=dep_chain))

            # special case for include tasks, where the include params
            # may be specified in the vars field for the task, which should
            # have higher precedence than the vars/np facts above
            all_vars = combine_vars(all_vars, task.get_include_params())

        # finally, we merge in extra vars and the magic variables
        all_vars = combine_vars(all_vars, self._extra_vars)
        all_vars = combine_vars(all_vars, magic_variables)

        # special case for the 'environment' magic variable, as someone
        # may have set it as a variable and we don't want to stomp on it
        if task:
            if  'environment' not in all_vars:
                all_vars['environment'] = task.environment
            else:
                display.warning("The variable 'environment' appears to be used already, which is also used internally for environment variables set on the task/block/play. You should use a different variable name to avoid conflicts with this internal variable")

        # if we have a task and we're delegating to another host, figure out the
        # variables for that host now so we don't have to rely on hostvars later
        if task and task.delegate_to is not None and include_delegate_to:
            all_vars['ansible_delegated_vars'] = self._get_delegated_vars(loader, play, task, all_vars)

        #VARIABLE_CACHE[cache_entry] = all_vars
        if task or play:
            all_vars['vars'] = all_vars.copy()

        display.debug("done with get_vars()")
        return all_vars