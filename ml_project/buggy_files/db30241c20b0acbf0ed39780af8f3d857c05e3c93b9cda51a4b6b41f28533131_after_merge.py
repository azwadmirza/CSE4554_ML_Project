    def get_fname(query):
        data = subprocess.check_output(["fc-match", "-v", query])
        if six.PY2:
            data = data.decode('UTF-8')
        for line in data.splitlines():
            line = line.strip()
            if line.startswith("file: "):
                return line.split('"')[1]
        return None