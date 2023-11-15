    def load_flows_file(self, path):
        path = os.path.expanduser(path)
        try:
            f = file(path, "rb")
            freader = FlowReader(f)
        except IOError as v:
            raise FlowReadError(v.strerror)
        return self.load_flows(freader)