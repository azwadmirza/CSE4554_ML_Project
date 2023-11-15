    def get_user_requests(self):
        """
        return a list of user requested items.  Each item is a dict with the
        following keys:
        'date': the date and time running the command
        'cmd': a list of argv of the actual command which was run
        'action': install/remove/update
        'specs': the specs being used
        """
        res = []
        com_pat = re.compile(r'#\s*cmd:\s*(.+)')
        spec_pat = re.compile(r'#\s*(\w+)\s*specs:\s*(.+)?')
        for dt, unused_cont, comments in self.parse():
            item = {'date': dt}
            for line in comments:
                m = com_pat.match(line)
                if m:
                    argv = m.group(1).split()
                    if argv[0].endswith('conda'):
                        argv[0] = 'conda'
                    item['cmd'] = argv
                m = spec_pat.match(line)
                if m:
                    action, specs = m.groups()
                    item['action'] = action
                    specs = specs or ""
                    if specs.startswith('['):
                        specs = literal_eval(specs)
                    elif '[' not in specs:
                        specs = specs.split(',')
                    specs = [spec for spec in specs if spec and not spec.endswith('@')]
                    if specs and action in ('update', 'install', 'create'):
                        item['update_specs'] = item['specs'] = specs
                    elif specs and action in ('remove', 'uninstall'):
                        item['remove_specs'] = item['specs'] = specs

            if 'cmd' in item:
                res.append(item)
            dists = groupby(itemgetter(0), unused_cont)
            item['unlink_dists'] = dists.get('-', ())
            item['link_dists'] = dists.get('+', ())
        return res