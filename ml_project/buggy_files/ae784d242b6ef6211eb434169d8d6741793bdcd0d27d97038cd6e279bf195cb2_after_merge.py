    def head(self, kernel_name, path):
        return self.get(kernel_name, path, include_body=False)