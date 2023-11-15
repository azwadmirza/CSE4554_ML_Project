    def head(self, kernel_name, path):
        self.get(kernel_name, path, include_body=False)