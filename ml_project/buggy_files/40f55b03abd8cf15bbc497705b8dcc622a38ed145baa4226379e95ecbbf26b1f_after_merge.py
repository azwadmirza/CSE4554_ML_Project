    def get_family(query):
        data = subprocess.check_output(["fc-match", query])
        if six.PY2:
            data = data.decode('UTF-8')
        for line in data.splitlines():
            line = line.strip()
            if not line:
                continue
            fname, family, _, variant = line.split('"')[:4]
            family = family.replace('"', '')
            if family:
                return family
        return None