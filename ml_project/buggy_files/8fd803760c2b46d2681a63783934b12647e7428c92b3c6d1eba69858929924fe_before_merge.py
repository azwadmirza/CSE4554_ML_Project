    def _parse_requirements_file(self, requirements_file, allow_old_format=True):
        """
        Parses an Ansible requirement.yml file and returns all the roles and/or collections defined in it. There are 2
        requirements file format:

            # v1 (roles only)
            - src: The source of the role, required if include is not set. Can be Galaxy role name, URL to a SCM repo or tarball.
              name: Downloads the role to the specified name, defaults to Galaxy name from Galaxy or name of repo if src is a URL.
              scm: If src is a URL, specify the SCM. Only git or hd are supported and defaults ot git.
              version: The version of the role to download. Can also be tag, commit, or branch name and defaults to master.
              include: Path to additional requirements.yml files.

            # v2 (roles and collections)
            ---
            roles:
            # Same as v1 format just under the roles key

            collections:
            - namespace.collection
            - name: namespace.collection
              version: version identifier, multiple identifiers are separated by ','
              source: the URL or a predefined source name that relates to C.GALAXY_SERVER_LIST

        :param requirements_file: The path to the requirements file.
        :param allow_old_format: Will fail if a v1 requirements file is found and this is set to False.
        :return: a dict containing roles and collections to found in the requirements file.
        """
        requirements = {
            'roles': [],
            'collections': [],
        }

        b_requirements_file = to_bytes(requirements_file, errors='surrogate_or_strict')
        if not os.path.exists(b_requirements_file):
            raise AnsibleError("The requirements file '%s' does not exist." % to_native(requirements_file))

        display.vvv("Reading requirement file at '%s'" % requirements_file)
        with open(b_requirements_file, 'rb') as req_obj:
            try:
                file_requirements = yaml.safe_load(req_obj)
            except YAMLError as err:
                raise AnsibleError(
                    "Failed to parse the requirements yml at '%s' with the following error:\n%s"
                    % (to_native(requirements_file), to_native(err)))

        if requirements_file is None:
            raise AnsibleError("No requirements found in file '%s'" % to_native(requirements_file))

        def parse_role_req(requirement):
            if "include" not in requirement:
                role = RoleRequirement.role_yaml_parse(requirement)
                display.vvv("found role %s in yaml file" % to_text(role))
                if "name" not in role and "src" not in role:
                    raise AnsibleError("Must specify name or src for role")
                return [GalaxyRole(self.galaxy, self.api, **role)]
            else:
                b_include_path = to_bytes(requirement["include"], errors="surrogate_or_strict")
                if not os.path.isfile(b_include_path):
                    raise AnsibleError("Failed to find include requirements file '%s' in '%s'"
                                       % (to_native(b_include_path), to_native(requirements_file)))

                with open(b_include_path, 'rb') as f_include:
                    try:
                        return [GalaxyRole(self.galaxy, self.api, **r) for r in
                                (RoleRequirement.role_yaml_parse(i) for i in yaml.safe_load(f_include))]
                    except Exception as e:
                        raise AnsibleError("Unable to load data from include requirements file: %s %s"
                                           % (to_native(requirements_file), to_native(e)))

        if isinstance(file_requirements, list):
            # Older format that contains only roles
            if not allow_old_format:
                raise AnsibleError("Expecting requirements file to be a dict with the key 'collections' that contains "
                                   "a list of collections to install")

            for role_req in file_requirements:
                requirements['roles'] += parse_role_req(role_req)

        else:
            # Newer format with a collections and/or roles key
            extra_keys = set(file_requirements.keys()).difference(set(['roles', 'collections']))
            if extra_keys:
                raise AnsibleError("Expecting only 'roles' and/or 'collections' as base keys in the requirements "
                                   "file. Found: %s" % (to_native(", ".join(extra_keys))))

            for role_req in file_requirements.get('roles', []):
                requirements['roles'] += parse_role_req(role_req)

            for collection_req in file_requirements.get('collections', []):
                if isinstance(collection_req, dict):
                    req_name = collection_req.get('name', None)
                    if req_name is None:
                        raise AnsibleError("Collections requirement entry should contain the key name.")

                    req_version = collection_req.get('version', '*')
                    req_source = collection_req.get('source', None)
                    if req_source:
                        # Try and match up the requirement source with our list of Galaxy API servers defined in the
                        # config, otherwise create a server with that URL without any auth.
                        req_source = next(iter([a for a in self.api_servers if req_source in [a.name, a.api_server]]),
                                          GalaxyAPI(self.galaxy, "explicit_requirement_%s" % req_name, req_source))

                    requirements['collections'].append((req_name, req_version, req_source))
                else:
                    requirements['collections'].append((collection_req, '*', None))

        return requirements