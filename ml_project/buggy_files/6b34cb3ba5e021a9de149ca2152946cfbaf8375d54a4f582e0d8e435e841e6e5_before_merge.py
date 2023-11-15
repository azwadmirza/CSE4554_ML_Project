    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)

        account = self.app.client_manager.get_account()
        container = parsed_args.container

        data = self.app.client_manager.storage.container_show(
            account, container)

        data_dir = self.app.client_manager.directory.get(
            account, container)

        info = {'account': data['system']['sys.account'],
                'base_name': data['system']['sys.name'],
                'name': data['system']['sys.user.name'],
                'meta0': list(),
                'meta1': list(),
                'meta2': list()}

        for d in data_dir['srv']:
            if d['type'] == 'meta2':
                info['meta2'].append(d['host'])

        for d in data_dir['dir']:
            if d['type'] == 'meta0':
                info['meta0'].append(d['host'])
            if d['type'] == 'meta1':
                info['meta1'].append(d['host'])

        for stype in ["meta0", "meta1", "meta2"]:
            info[stype] = ', '.join(info[stype])
        return zip(*sorted(info.iteritems()))