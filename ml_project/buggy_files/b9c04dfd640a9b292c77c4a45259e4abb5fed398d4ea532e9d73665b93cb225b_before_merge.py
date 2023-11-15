    def training_step_end(self, output):
        if isinstance(output, Result):
            output.dp_reduce()
        return output