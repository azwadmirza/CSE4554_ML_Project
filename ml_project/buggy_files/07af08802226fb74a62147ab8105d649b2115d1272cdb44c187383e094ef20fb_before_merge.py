    def __str__(self):
        """String representation of an input/output system"""
        str = "System: " + (self.name if self.name else "(none)") + "\n"
        str += "Inputs (%d): " % self.ninputs
        for key in self.input_index: str += key + ", "
        str += "\nOutputs (%d): " % self.noutputs
        for key in self.output_index: str += key + ", "
        str += "\nStates (%d): " % self.nstates
        for key in self.state_index: str += key + ", "
        return str