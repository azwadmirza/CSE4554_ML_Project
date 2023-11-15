    def edit_config(self, candidate=None, commit=True, replace=None, comment=None):

        operations = self.get_device_operations()
        self.check_edit_config_capabiltiy(operations, candidate, commit, replace, comment)

        resp = {}
        results = []
        requests = []

        if replace:
            candidate = 'load replace {0}'.format(replace)

        for line in to_list(candidate):
            if not isinstance(line, collections.Mapping):
                line = {'command': line}
            cmd = line['command']
            results.append(self.send_command(**line))
            requests.append(cmd)

        diff = self.compare_configuration()
        if diff:
            resp['diff'] = diff

        if commit:
            self.commit(comment=comment)
        else:
            self.discard_changes()

        resp['request'] = requests
        resp['response'] = results
        return resp