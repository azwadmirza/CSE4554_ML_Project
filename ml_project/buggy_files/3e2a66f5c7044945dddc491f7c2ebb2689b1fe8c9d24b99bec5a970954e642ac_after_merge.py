    def run_commands(self, commands, check_rc=True):
        """Run list of commands on remote device and return results
        """
        responses = list()

        for item in to_list(commands):
            if item['output'] == 'json' and not is_json(item['command']):
                cmd = '%s | json' % item['command']
            elif item['output'] == 'text' and is_json(item['command']):
                cmd = item['command'].rsplit('|', 1)[0]
            else:
                cmd = item['command']

            rc, out, err = self.exec_command(cmd)
            try:
                out = to_text(out, errors='surrogate_or_strict')
            except UnicodeError:
                self._module.fail_json(msg=u'Failed to decode output from %s: %s' % (cmd, to_text(out)))

            if check_rc and rc != 0:
                self._module.fail_json(msg=to_text(err))

            if not check_rc and rc != 0:
                try:
                    out = self._module.from_json(err)
                except ValueError:
                    out = to_text(err).strip()
            else:
                try:
                    out = self._module.from_json(out)
                except ValueError:
                    out = to_text(out).strip()

            if item['output'] == 'json' and isinstance(out, string_types):
                self._module.fail_json(msg='failed to retrieve output of %s in json format' % item['command'])

            responses.append(out)
        return responses