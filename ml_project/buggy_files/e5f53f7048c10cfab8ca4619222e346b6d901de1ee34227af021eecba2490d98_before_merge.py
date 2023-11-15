    def _get_hostgroup_vars(self, host=None, group=None, new_pb_basedir=False):
        """
        Loads variables from group_vars/<groupname> and host_vars/<hostname> in directories parallel
        to the inventory base directory or in the same directory as the playbook.  Variables in the playbook
        dir will win over the inventory dir if files are in both.
        """

        results = {}
        scan_pass = 0
        _basedir = self.basedir()

        # look in both the inventory base directory and the playbook base directory
        # unless we do an update for a new playbook base dir
        if not new_pb_basedir:
            basedirs = [_basedir, self._playbook_basedir]
        else:
            basedirs = [self._playbook_basedir]

        for basedir in basedirs:
            # this can happen from particular API usages, particularly if not run
            # from /usr/bin/ansible-playbook
            if basedir in ('', None):
                basedir = './'

            scan_pass = scan_pass + 1

            # it's not an eror if the directory does not exist, keep moving
            if not os.path.exists(basedir):
                continue

            # save work of second scan if the directories are the same
            if _basedir == self._playbook_basedir and scan_pass != 1:
                continue

            if group and host is None:
                # load vars in dir/group_vars/name_of_group
                base_path = os.path.realpath(os.path.join(basedir, "group_vars/%s" % group.name))
                results = combine_vars(results, self._variable_manager.add_group_vars_file(base_path, self._loader))
            elif host and group is None:
                # same for hostvars in dir/host_vars/name_of_host
                base_path = os.path.realpath(os.path.join(basedir, "host_vars/%s" % host.name))
                results = combine_vars(results, self._variable_manager.add_host_vars_file(base_path, self._loader))

        # all done, results is a dictionary of variables for this particular host.
        return results