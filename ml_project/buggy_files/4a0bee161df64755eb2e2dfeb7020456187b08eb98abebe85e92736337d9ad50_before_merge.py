    def parse_interfaces(self, data):
        objects = list()
        for item in data['TABLE_interface']['ROW_interface']:
            objects.append(item['interface'])
        return objects