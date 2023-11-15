    def _print_summary(self):
        string = "\n\tTitle: "
        string += self.metadata.General.title.decode('utf8')
        if self.metadata.has_item("Signal.signal_type"):
            string += "\n\tSignal type: "
            string += self.metadata.Signal.signal_type
        string += "\n\tData dimensions: "
        string += str(self.axes_manager.shape)
        if self.metadata.has_item('Signal.record_by'):
            string += "\n\tData representation: "
            string += self.metadata.Signal.record_by
            string += "\n\tData type: "
            string += str(self.data.dtype)
        print(string)