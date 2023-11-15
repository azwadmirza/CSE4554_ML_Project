    def get_vars(self, loader, play=None, host=None, task=None, include_hostvars=True, use_cache=True):
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

        debug("in VariableManager get_vars()")
        cache_entry = self._get_cache_entry(play=play, host=host, task=task)
        if cache_entry in CACHED_VARS and use_cache:
            debug("vars are cached, returning them now")
            return CACHED_VARS[cache_entry]

        all_vars = defaultdict(dict)

        if play:
            # first we compile any vars specified in defaults/main.yml
            # for all roles within the specified play
            for role in play.get_roles():
                all_vars = combine_vars(all_vars, role.get_default_vars())

            # if we have a task in this context, and that task has a role, make
            # sure it sees its defaults above any other roles, as we previously
            # (v1) made sure each task had a copy of its roles default vars
            if task and task._role is not None:
                all_vars = combine_vars(all_vars, task._role.get_default_vars())

        if host:
            # next, if a host is specified, we load any vars from group_vars
            # files and then any vars from host_vars files which may apply to
            # this host or the groups it belongs to

            # we merge in vars from groups specified in the inventory (INI or script)
            all_vars = combine_vars(all_vars, host.get_group_vars())

            # then we merge in the special 'all' group_vars first, if they exist
            if 'all' in self._group_vars_files:
                data = self._preprocess_vars(self._group_vars_files['all'])
                for item in data:
                    all_vars = combine_vars(all_vars, item)

            for group in host.get_groups():
                if group.name in self._group_vars_files and group.name != 'all':
                    for data in self._group_vars_files[group.name]:
                        data = self._preprocess_vars(data)
                        for item in data:
                            all_vars = combine_vars(all_vars, item)

            # then we merge in vars from the host specified in the inventory (INI or script)
            all_vars = combine_vars(all_vars, host.get_vars())

            # then we merge in the host_vars/<hostname> file, if it exists
            host_name = host.get_name()
            if host_name in self._host_vars_files:
                for data in self._host_vars_files[host_name]:
                    data = self._preprocess_vars(data)
                    for item in data:
                        all_vars = combine_vars(all_vars, item)

            # finally, the facts cache for this host, if it exists
            try:
                host_facts = self._fact_cache.get(host.name, dict())
                for k in host_facts.keys():
                    if not isinstance(host_facts[k], UnsafeProxy):
                        host_facts[k] = UnsafeProxy(host_facts[k])
                all_vars = combine_vars(all_vars, host_facts)
            except KeyError:
                pass

        if play:
            all_vars = combine_vars(all_vars, play.get_vars())

            for vars_file_item in play.get_vars_files():
                try:
                    # create a set of temporary vars here, which incorporate the
                    # extra vars so we can properly template the vars_files entries
                    temp_vars = combine_vars(all_vars, self._extra_vars)
                    templar = Templar(loader=loader, variables=temp_vars)

                    # we assume each item in the list is itself a list, as we
                    # support "conditional includes" for vars_files, which mimics
                    # the with_first_found mechanism.
                    vars_file_list = templar.template(vars_file_item)
                    if not isinstance(vars_file_list, list):
                         vars_file_list = [ vars_file_list ]

                    # now we iterate through the (potential) files, and break out
                    # as soon as we read one from the list. If none are found, we
                    # raise an error, which is silently ignored at this point.
                    for vars_file in vars_file_list:
                        data = self._preprocess_vars(loader.load_from_file(vars_file))
                        if data is not None:
                            for item in data:
                                all_vars = combine_vars(all_vars, item)
                            break
                    else:
                        raise AnsibleError("vars file %s was not found" % vars_file_item)
                except UndefinedError:
                    continue

            if not C.DEFAULT_PRIVATE_ROLE_VARS:
                for role in play.get_roles():
                    all_vars = combine_vars(all_vars, role.get_vars())

        if task:
            if task._role:
                all_vars = combine_vars(all_vars, task._role.get_vars())
            all_vars = combine_vars(all_vars, task.get_vars())

        if host:
            all_vars = combine_vars(all_vars, self._vars_cache.get(host.get_name(), dict()))

        all_vars = combine_vars(all_vars, self._extra_vars)

        # FIXME: make sure all special vars are here
        # Finally, we create special vars

        all_vars['playbook_dir'] = loader.get_basedir()

        if host:
            all_vars['groups'] = [group.name for group in host.get_groups()]

            if self._inventory is not None:
                all_vars['groups']   = self._inventory.groups_list()
                if include_hostvars:
                    hostvars = HostVars(vars_manager=self, play=play, inventory=self._inventory, loader=loader)
                    all_vars['hostvars'] = hostvars

        if task:
            if task._role:
                all_vars['role_path'] = task._role._role_path

        if self._inventory is not None:
            all_vars['inventory_dir'] = self._inventory.basedir()
            if play:
                # add the list of hosts in the play, as adjusted for limit/filters
                # DEPRECATED: play_hosts should be deprecated in favor of ansible_play_hosts,
                #             however this would take work in the templating engine, so for now
                #             we'll add both so we can give users something transitional to use
                host_list = [x.name for x in self._inventory.get_hosts()]
                all_vars['play_hosts'] = host_list
                all_vars['ansible_play_hosts'] = host_list


        # the 'omit' value alows params to be left out if the variable they are based on is undefined
        all_vars['omit'] = self._omit_token

        all_vars['ansible_version'] = CLI.version_info(gitinfo=False)

        if 'hostvars' in all_vars and host:
            all_vars['vars'] = all_vars['hostvars'][host.get_name()]

        #CACHED_VARS[cache_entry] = all_vars

        debug("done with get_vars()")
        return all_vars