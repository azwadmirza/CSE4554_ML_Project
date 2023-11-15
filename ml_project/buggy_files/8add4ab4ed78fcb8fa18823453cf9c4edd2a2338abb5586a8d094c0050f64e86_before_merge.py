    def _load_tasks(self, tasks, vars={}, default_vars={}, sudo_vars={}, additional_conditions=[], original_file=None):
        ''' handle task and handler include statements '''

        results = []
        if tasks is None:
            # support empty handler files, and the like.
            tasks = []

        for x in tasks:
            if not isinstance(x, dict):
                raise errors.AnsibleError("expecting dict; got: %s" % x)

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
                    results.append(Task(self,x))
                    continue

            task_vars = self.vars.copy()
            task_vars.update(vars)
            if original_file:
                task_vars['_original_file'] = original_file

            if 'include' in x:
                tokens = shlex.split(str(x['include']))
                items = ['']
                included_additional_conditions = list(additional_conditions)
                for k in x:
                    if k.startswith("with_"):
                        plugin_name = k[5:]
                        if plugin_name not in utils.plugins.lookup_loader:
                            raise errors.AnsibleError("cannot find lookup plugin named %s for usage in with_%s" % (plugin_name, plugin_name))
                        terms = template(self.basedir, x[k], task_vars)
                        items = utils.plugins.lookup_loader.get(plugin_name, basedir=self.basedir, runner=None).run(terms, inject=task_vars)
                    elif k.startswith("when_"):
                        included_additional_conditions.insert(0, utils.compile_when_to_only_if("%s %s" % (k[5:], x[k])))
                    elif k == 'when':
                        included_additional_conditions.insert(0, utils.compile_when_to_only_if("jinja2_compare %s" % x[k]))
                    elif k in ("include", "vars", "default_vars", "only_if", "sudo", "sudo_user"):
                        pass
                    else:
                        raise errors.AnsibleError("parse error: task includes cannot be used with other directives: %s" % k)

                default_vars = utils.combine_vars(self.default_vars, x.get('default_vars', {}))
                if 'vars' in x:
                    task_vars = utils.combine_vars(task_vars, x['vars'])
                if 'only_if' in x:
                    included_additional_conditions.append(x['only_if'])

                for item in items:
                    mv = task_vars.copy()
                    mv['item'] = item
                    for t in tokens[1:]:
                        (k,v) = t.split("=", 1)
                        mv[k] = template(self.basedir, v, mv)
                    dirname = self.basedir
                    if original_file:
                        dirname = os.path.dirname(original_file)
                    include_file = template(dirname, tokens[0], mv)
                    include_filename = utils.path_dwim(dirname, include_file)
                    data = utils.parse_yaml_from_file(include_filename)
                    results += self._load_tasks(data, mv, default_vars, included_sudo_vars, included_additional_conditions, original_file=include_filename)
            elif type(x) == dict:
                results.append(Task(self,x,module_vars=task_vars,default_vars=default_vars,additional_conditions=additional_conditions))
            else:
                raise Exception("unexpected task type")

        for x in results:
            if self.tags is not None:
                x.tags.extend(self.tags)

        return results