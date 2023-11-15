    def on_core_read_ready(self):
        raw_output = bytes(self.core_process.readAll())
        if b'Traceback' in raw_output:
            self.core_traceback = raw_output.decode()
        print(raw_output.decode().strip())