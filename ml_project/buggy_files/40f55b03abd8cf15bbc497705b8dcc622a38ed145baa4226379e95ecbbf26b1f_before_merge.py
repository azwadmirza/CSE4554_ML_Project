    def get_family(query):
        data = os.popen("fc-match \"%s\""%query, "r").read()
        for line in data.splitlines():
            line = line.strip()
            if not line:
                continue
            fname, family, _, variant = line.split('"')[:4]
            family = family.replace('"', '')
            if family:
                return family
        return None