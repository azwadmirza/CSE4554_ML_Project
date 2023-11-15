    def execute_install(self):
        """
        Executes the installation action. The args list contains the
        roles to be installed, unless -f was specified. The list of roles
        can be a name (which will be downloaded via the galaxy API and github),
        or it can be a local .tar.gz file.
        """

        role_file  = self.get_opt("role_file", None)

        if len(self.args) == 0 and role_file is None:
            # the user needs to specify one of either --role-file
            # or specify a single user/role name
            raise AnsibleOptionsError("- you must specify a user/role name or a roles file")
        elif len(self.args) == 1 and not role_file is None:
            # using a role file is mutually exclusive of specifying
            # the role name on the command line
            raise AnsibleOptionsError("- please specify a user/role name, or a roles file, but not both")

        no_deps    = self.get_opt("no_deps", False)
        roles_path = self.get_opt("roles_path")

        roles_done = []
        roles_left = []
        if role_file:
            f = open(role_file, 'r')
            if role_file.endswith('.yaml') or role_file.endswith('.yml'):
                roles_left = map(ansible.utils.role_yaml_parse, yaml.safe_load(f))
            else:
                # roles listed in a file, one per line
                for rname in f.readlines():
                    roles_left.append(GalaxyRole(self.galaxy, rname.strip()))
            f.close()
        else:
            # roles were specified directly, so we'll just go out grab them
            # (and their dependencies, unless the user doesn't want us to).
            for rname in self.args:
                roles_left.append(GalaxyRole(self.galaxy, rname.strip()))

        while len(roles_left) > 0:
            # query the galaxy API for the role data
            role_data = None
            role = roles_left.pop(0)
            role_path = role.path

            if role_path:
                self.options.roles_path = role_path
            else:
                self.options.roles_path = roles_path

            tmp_file = None
            installed = False
            if role.src and os.path.isfile(role.src):
                # installing a local tar.gz
                tmp_file = role.src
            else:
                if role.scm:
                    # create tar file from scm url
                    tmp_file = scm_archive_role(role.scm, role.src, role.version, role.name)
                if role.src:
                    if '://' not in role.src:
                        role_data = self.api.lookup_role_by_name(role.src)
                        if not role_data:
                            self.display.warning("- sorry, %s was not found on %s." % (role.src, self.options.api_server))
                            self.exit_without_ignore()
                            continue

                        role_versions = self.api.fetch_role_related('versions', role_data['id'])
                        if not role.version:
                            # convert the version names to LooseVersion objects
                            # and sort them to get the latest version. If there
                            # are no versions in the list, we'll grab the head
                            # of the master branch
                            if len(role_versions) > 0:
                                loose_versions = [LooseVersion(a.get('name',None)) for a in role_versions]
                                loose_versions.sort()
                                role.version = str(loose_versions[-1])
                            else:
                                role.version = 'master'
                        elif role.version != 'master':
                            if role_versions and role.version not in [a.get('name', None) for a in role_versions]:
                                self.display.warning('role is %s' % role)
                                self.display.warning("- the specified version (%s) was not found in the list of available versions (%s)." % (role.version, role_versions))
                                self.exit_without_ignore()
                                continue

                    # download the role. if --no-deps was specified, we stop here,
                    # otherwise we recursively grab roles and all of their deps.
                    tmp_file = role.fetch(role_data)
            if tmp_file:
                installed = role.install(tmp_file)
                # we're done with the temp file, clean it up
                if tmp_file != role.src:
                    os.unlink(tmp_file)
                # install dependencies, if we want them

                # this should use new roledepenencies code
                #if not no_deps and installed:
                #    if not role_data:
                #        role_data = gr.get_metadata(role.get("name"), options)
                #        role_dependencies = role_data['dependencies']
                #    else:
                #        role_dependencies = role_data['summary_fields']['dependencies'] # api_fetch_role_related(api_server, 'dependencies', role_data['id'])
                #    for dep in role_dependencies:
                #        if isinstance(dep, basestring):
                #            dep = ansible.utils.role_spec_parse(dep)
                #        else:
                #            dep = ansible.utils.role_yaml_parse(dep)
                #        if not get_role_metadata(dep["name"], options):
                #            if dep not in roles_left:
                #                print '- adding dependency: %s' % dep["name"]
                #                roles_left.append(dep)
                #            else:
                #                print '- dependency %s already pending installation.' % dep["name"]
                #        else:
                #            print '- dependency %s is already installed, skipping.' % dep["name"]

            if not tmp_file or not installed:
                self.display.warning("- %s was NOT installed successfully." % role.name)
                self.exit_without_ignore()
        return 0