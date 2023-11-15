    def _load_tasks(self, tasks, vars=None, default_vars=None, sudo_vars=None,
                    additional_conditions=None, original_file=None, role_name=None):
        ''' handle task and handler include statements '''

        results = []
        if tasks is None:
            # support empty handler files, and the like.
            tasks = []
        if additional_conditions is None:
            additional_conditions = []
        if vars is None:
            vars = {}
        if default_vars is None:
            default_vars = {}
        if sudo_vars is None:
            sudo_vars = {}

        old_conditions = list(additional_conditions)

        for x in tasks:

            # prevent assigning the same conditions to each task on an include
            included_additional_conditions = list(old_conditions)

            if not isinstance(x, dict):
                raise errors.AnsibleError("expecting dict; got: %s, error in %s" % (x, original_file))

            # evaluate sudo vars for current and child tasks 
            included_sudo_vars = {}
            for k in ["sudo", "sudo_user"]:
                if k in x:
                    included_sudo_vars[k] = x[k]
                elif k in sudo_vars:
                    included_sudo_vars[k] = sudo_vars[k]
                    x[k] = sudo_vars[k]

            if 'meta' in x:
                if x['meta'] == 'flush_handlers':
                    results.append(Task(self, x))
                    continue

            task_vars = self.vars.copy()
            task_vars.update(vars)
            if original_file:
                task_vars['_original_file'] = original_file

            if 'include' in x:
                tokens = utils.splitter.split_args(str(x['include']))
                included_additional_conditions = list(additional_conditions)
                include_vars = {}
                for k in x:
                    if k.startswith("with_"):
                        if original_file:
                            offender = " (in %s)" % original_file
                        else:
                            offender = ""
                        utils.deprecated("include + with_items is a removed deprecated feature" + offender, "1.5", removed=True)
                    elif k.startswith("when_"):
                        utils.deprecated("\"when_<criteria>:\" is a removed deprecated feature, use the simplified 'when:' conditional directly", None, removed=True)
                    elif k == 'when':
                        if type(x[k]) is str:
                            included_additional_conditions.insert(0, x[k])
                        elif type(x[k]) is list:
                            for i in x[k]:
                                included_additional_conditions.insert(0, i)
                    elif k in ("include", "vars", "default_vars", "sudo", "sudo_user", "role_name", "no_log"):
                        continue
                    else:
                        include_vars[k] = x[k]

                default_vars = x.get('default_vars', {})
                if not default_vars:
                    default_vars = self.default_vars
                else:
                    default_vars = utils.combine_vars(self.default_vars, default_vars)

                # append the vars defined with the include (from above) 
                # as well as the old-style 'vars' element. The old-style
                # vars are given higher precedence here (just in case)
                task_vars = utils.combine_vars(task_vars, include_vars)
                if 'vars' in x:
                    task_vars = utils.combine_vars(task_vars, x['vars'])

                if 'when' in x:
                    if isinstance(x['when'], (basestring, bool)):
                        included_additional_conditions.append(x['when'])
                    elif isinstance(x['when'], list):
                        included_additional_conditions.extend(x['when'])

                new_role = None
                if 'role_name' in x:
                    new_role = x['role_name']

                mv = task_vars.copy()
                for t in tokens[1:]:
                    (k,v) = t.split("=", 1)
                    mv[k] = template(self.basedir, v, mv)
                dirname = self.basedir
                if original_file:
                    dirname = os.path.dirname(original_file)
                include_file = template(dirname, tokens[0], mv)
                include_filename = utils.path_dwim(dirname, include_file)
                data = utils.parse_yaml_from_file(include_filename, vault_password=self.vault_password)
                if 'role_name' in x and data is not None:
                    for y in data:
                        if isinstance(y, dict) and 'include' in y:
                            y['role_name'] = new_role
                loaded = self._load_tasks(data, mv, default_vars, included_sudo_vars, list(included_additional_conditions), original_file=include_filename, role_name=new_role)
                results += loaded
            elif type(x) == dict:
                task = Task(
                    self, x,
                    module_vars=task_vars,
                    default_vars=default_vars,
                    additional_conditions=list(additional_conditions),
                    role_name=role_name
                )
                results.append(task)
            else:
                raise Exception("unexpected task type")

        for x in results:
            if self.tags is not None:
                x.tags.extend(self.tags)

        return results