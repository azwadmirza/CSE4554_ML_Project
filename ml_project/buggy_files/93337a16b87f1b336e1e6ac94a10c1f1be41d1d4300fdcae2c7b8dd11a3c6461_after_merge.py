    def load_flows_file(self, path):
        path = os.path.expanduser(path)
        try:
            with open(path, "rb") as f:
                freader = FlowReader(f)
                return self.load_flows(freader)
        except IOError as v:
            raise FlowReadError(v.strerror)