    def write_initial(self, msg, obj_index):
        if msg is None:
            return
        self.stream.write("{:<{width}} ... \r\n".format(
            msg + ' ' + obj_index, width=self.width))
        self.stream.flush()