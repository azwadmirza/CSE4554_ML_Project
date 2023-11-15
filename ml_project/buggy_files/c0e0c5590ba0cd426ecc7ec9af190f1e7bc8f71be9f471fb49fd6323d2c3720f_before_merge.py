    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)

        if 'msg' in self._task.args:
            if 'fail' in self._task.args and boolean(self._task.args['fail']):
                result['failed'] = True
                result['msg'] = self._task.args['msg']
            else:
                result['msg'] = self._task.args['msg']
        # FIXME: move the LOOKUP_REGEX somewhere else
        elif 'var' in self._task.args: # and not utils.LOOKUP_REGEX.search(self._task.args['var']):
            results = self._templar.template(self._task.args['var'], convert_bare=True)
            if results == self._task.args['var']:
                results = "VARIABLE IS NOT DEFINED!"
            result[self._task.args['var']] = results
        else:
            result['msg'] = 'here we are'

        # force flag to make debug output module always verbose
        result['_ansible_verbose_always'] = True

        return result