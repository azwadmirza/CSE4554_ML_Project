    def get_fname(query):
        data = os.popen("fc-match -v \"%s\""%query, "r").read()
        for line in data.splitlines():
            line = line.strip()
            if line.startswith("file: "):
                return line.split('"')[1]
        return None