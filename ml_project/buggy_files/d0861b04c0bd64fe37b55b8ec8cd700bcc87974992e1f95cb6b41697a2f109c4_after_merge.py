    def populate(self):
        data = None

        try:
            data = self.run('show version', output='json')
        except ConnectionError:
            data = self.run('show version')
        if data:
            if isinstance(data, dict):
                if data.get('sys_ver_str'):
                    self.facts.update(self.transform_dict(data, self.VERSION_MAP_7K))
                else:
                    self.facts.update(self.transform_dict(data, self.VERSION_MAP))
            else:
                self.facts['version'] = self.parse_version(data)
                self.facts['serialnum'] = self.parse_serialnum(data)
                self.facts['model'] = self.parse_model(data)
                self.facts['image'] = self.parse_image(data)
                self.facts['hostname'] = self.parse_hostname(data)