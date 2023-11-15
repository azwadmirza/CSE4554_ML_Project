    def validation_step_end(self, output):
        if isinstance(output, Result):
            output.dp_reduce()
        elif isinstance(output, torch.Tensor):
            output = output.mean()
        return output