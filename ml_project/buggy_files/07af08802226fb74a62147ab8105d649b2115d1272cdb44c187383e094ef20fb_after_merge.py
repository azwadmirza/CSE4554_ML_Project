    def __str__(self):
        """String representation of an input/output system"""
        str = "System: " + (self.name if self.name else "(None)") + "\n"
        str += "Inputs (%s): " % self.ninputs
        for key in self.input_index: str += key + ", "
        str += "\nOutputs (%s): " % self.noutputs
        for key in self.output_index: str += key + ", "
        str += "\nStates (%s): " % self.nstates
        for key in self.state_index: str += key + ", "
        return str