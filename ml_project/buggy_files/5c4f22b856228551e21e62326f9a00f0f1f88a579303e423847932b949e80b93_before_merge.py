    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)

        if self._play_context.check_mode:
            result['skipped'] = True
            result['msg'] = 'check mode not supported for this module'
            return result

        # Parse out any hostname:port patterns
        new_name = self._task.args.get('name', self._task.args.get('hostname', None))
        display.vv("creating host via 'add_host': hostname=%s" % new_name)

        name, port = parse_address(new_name, allow_ranges=False)
        if not name:
            raise AnsibleError("Invalid inventory hostname: %s" % new_name)
        if port:
            self._task.args['ansible_ssh_port'] = port

        groups = self._task.args.get('groupname', self._task.args.get('groups', self._task.args.get('group', '')))
        # add it to the group if that was specified
        new_groups = []
        if groups:
            for group_name in groups.split(","):
                if group_name not in new_groups:
                    new_groups.append(group_name.strip())

        # Add any variables to the new_host
        host_vars = dict()
        special_args = frozenset(('name', 'hostname', 'groupname', 'groups'))
        for k in self._task.args.keys():
            if k not in special_args:
                host_vars[k] = self._task.args[k]

        result['changed'] = True
        result['add_host'] = dict(host_name=name, groups=new_groups, host_vars=host_vars)
        return result