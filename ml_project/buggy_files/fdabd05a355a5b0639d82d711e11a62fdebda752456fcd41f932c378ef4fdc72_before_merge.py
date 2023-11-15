    def do_POST(self):
        self.send_error(501, "Unsupported method (POST)")
        return