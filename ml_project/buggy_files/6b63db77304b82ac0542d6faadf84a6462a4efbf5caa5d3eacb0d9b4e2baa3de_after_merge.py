    def read_sysctl_file(self):

        lines = []
        if os.path.isfile(self.sysctl_file):
            try:
                with open(self.sysctl_file, "r") as read_file:
                    lines = read_file.readlines()
            except IOError as e:
                self.module.fail_json(msg="Failed to open %s: %s" % (self.sysctl_file, to_native(e)))

        for line in lines:
            line = line.strip()
            self.file_lines.append(line)

            # don't split empty lines or comments or line without equal sign
            if not line or line.startswith(("#", ";")) or "=" not in line:
                continue

            k, v = line.split('=', 1)
            k = k.strip()
            v = v.strip()
            self.file_values[k] = v.strip()