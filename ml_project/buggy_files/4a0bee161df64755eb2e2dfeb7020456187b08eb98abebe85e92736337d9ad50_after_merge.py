    def parse_interfaces(self, data):
        objects = list()
        for line in data.split('\n'):
            if len(line) == 0:
                continue
            elif line.startswith('admin') or line[0] == ' ':
                continue
            else:
                match = re.match(r'^(\S+)', line)
                if match:
                    intf = match.group(1)
                    if get_interface_type(intf) != 'unknown':
                        objects.append(intf)
        return objects