    def populate(self):
        data = self.run('show version', output='json')
        if data:
            if data.get('sys_ver_str'):
                self.facts.update(self.transform_dict(data, self.VERSION_MAP_7K))
            else:
                self.facts.update(self.transform_dict(data, self.VERSION_MAP))