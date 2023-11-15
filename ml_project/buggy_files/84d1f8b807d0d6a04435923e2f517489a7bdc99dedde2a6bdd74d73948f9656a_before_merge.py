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
        force      = self.get_opt('force', False)
        roles_path = self.get_opt("roles_path")

        roles_done = []
        roles_left = []
        if role_file:
            self.display.debug('Getting roles from %s' % role_file)
            try:
                self.display.debug('Processing role file: %s' % role_file)
                f = open(role_file, 'r')
                if role_file.endswith('.yaml') or role_file.endswith('.yml'):
                    try:
                        rolesparsed = map(self.parse_requirements_files, yaml.safe_load(f))
                    except Exception as e:
                       raise AnsibleError("%s does not seem like a valid yaml file: %s" % (role_file, str(e)))
                    roles_left = [GalaxyRole(self.galaxy, **r) for r in rolesparsed]
                else:
                    # roles listed in a file, one per line
                    self.display.deprecated("Non yaml files for role requirements")
                    for rname in f.readlines():
                        if rname.startswith("#") or rname.strip() == '':
                            continue
                        roles_left.append(GalaxyRole(self.galaxy, rname.strip()))
                f.close()
            except (IOError,OSError) as e:
                raise AnsibleError("Unable to read requirements file (%s): %s" % (role_file, str(e)))
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

            if role.install_info is not None and not force:
                self.display.display('- %s is already installed, skipping.' % role.name)
                continue

            if role_path:
                self.options.roles_path = role_path
            else:
                self.options.roles_path = roles_path

            self.display.debug('Installing role %s from %s' % (role.name, self.options.roles_path))

            tmp_file = None
            installed = False
            if role.src and os.path.isfile(role.src):
                # installing a local tar.gz
                tmp_file = role.src
            else:
                if role.scm:
                    # create tar file from scm url
                    tmp_file = GalaxyRole.scm_archive_role(role.scm, role.src, role.version, role.name)
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
                if not no_deps and installed:
                    role_dependencies = role.metadata.get('dependencies', [])
                    for dep in role_dependencies:
                        self.display.debug('Installing dep %s' % dep)
                        dep_req = RoleRequirement()
                        __, dep_name, __ = dep_req.parse(dep)
                        dep_role = GalaxyRole(self.galaxy, name=dep_name)
                        if dep_role.install_info is None or force:
                            if dep_role not in roles_left:
                                self.display.display('- adding dependency: %s' % dep_name)
                                roles_left.append(GalaxyRole(self.galaxy, name=dep_name))
                            else:
                                self.display.display('- dependency %s already pending installation.' % dep_name)
                        else:
                            self.display.display('- dependency %s is already installed, skipping.' % dep_name)

            if not tmp_file or not installed:
                self.display.warning("- %s was NOT installed successfully." % role.name)
                self.exit_without_ignore()
        return 0