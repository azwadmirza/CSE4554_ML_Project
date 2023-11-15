    def run(self, tmp=None, task_vars=None):

        if self._task.args.get('src'):
            try:
                self._handle_template()
            except ValueError as exc:
                return dict(failed=True, msg=to_text(exc))

        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp  # tmp no longer has any effect

        if self._task.args.get('backup') and result.get('__backup__'):
            # User requested backup and no error occurred in module.
            # NOTE: If there is a parameter error, _backup key may not be in results.
            filepath = self._write_backup(task_vars['inventory_hostname'],
                                          result['__backup__'])

            result['backup_path'] = filepath

        # strip out any keys that have two leading and two trailing
        # underscore characters
        for key in list(result.keys()):
            if PRIVATE_KEYS_RE.match(key):
                del result[key]

        return result