    def _build_role_dependencies(self, roles, dep_stack, passed_vars={}, level=0):
        # this number is arbitrary, but it seems sane
        if level > 20:
            raise errors.AnsibleError("too many levels of recursion while resolving role dependencies")
        for role in roles:
            role_path,role_vars = self._get_role_path(role)
            role_vars = utils.combine_vars(role_vars, passed_vars)
            vars = self._resolve_main(utils.path_dwim(self.basedir, os.path.join(role_path, 'vars')))
            vars_data = {}
            if os.path.isfile(vars):
                vars_data = utils.parse_yaml_from_file(vars)
                if vars_data:
                    role_vars = utils.combine_vars(vars_data, role_vars)
            defaults = self._resolve_main(utils.path_dwim(self.basedir, os.path.join(role_path, 'defaults')))
            defaults_data = {}
            if os.path.isfile(defaults):
                defaults_data = utils.parse_yaml_from_file(defaults)
            # the meta directory contains the yaml that should
            # hold the list of dependencies (if any)
            meta = self._resolve_main(utils.path_dwim(self.basedir, os.path.join(role_path, 'meta')))
            if os.path.isfile(meta):
                data = utils.parse_yaml_from_file(meta)
                if data:
                    dependencies = data.get('dependencies',[])
                    for dep in dependencies:
                        allow_dupes = False
                        (dep_path,dep_vars) = self._get_role_path(dep)
                        meta = self._resolve_main(utils.path_dwim(self.basedir, os.path.join(dep_path, 'meta')))
                        if os.path.isfile(meta):
                            meta_data = utils.parse_yaml_from_file(meta)
                            if meta_data:
                                allow_dupes = utils.boolean(meta_data.get('allow_duplicates',''))

                        if not allow_dupes:
                            if dep in self.included_roles:
                                continue
                            else:
                                self.included_roles.append(dep)

                        dep_vars = utils.combine_vars(passed_vars, dep_vars)
                        dep_vars = utils.combine_vars(role_vars, dep_vars)
                        vars = self._resolve_main(utils.path_dwim(self.basedir, os.path.join(dep_path, 'vars')))
                        vars_data = {}
                        if os.path.isfile(vars):
                            vars_data = utils.parse_yaml_from_file(vars)
                            if vars_data:
                                dep_vars = utils.combine_vars(vars_data, dep_vars)
                        defaults = self._resolve_main(utils.path_dwim(self.basedir, os.path.join(dep_path, 'defaults')))
                        dep_defaults_data = {}
                        if os.path.isfile(defaults):
                            dep_defaults_data = utils.parse_yaml_from_file(defaults)
                        if 'role' in dep_vars:
                            del dep_vars['role']
                        self._build_role_dependencies([dep], dep_stack, passed_vars=dep_vars, level=level+1)
                        dep_stack.append([dep,dep_path,dep_vars,dep_defaults_data])
            # only add the current role when we're at the top level,
            # otherwise we'll end up in a recursive loop 
            if level == 0:
                self.included_roles.append(role)
                dep_stack.append([role,role_path,role_vars,defaults_data])
        return dep_stack