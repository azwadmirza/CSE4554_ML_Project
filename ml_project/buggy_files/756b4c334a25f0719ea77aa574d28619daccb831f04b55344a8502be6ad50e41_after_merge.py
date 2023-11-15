    def record_success(self, execution_slice, job, outputs):
        super().record_success(execution_slice, job, outputs)
        if not self.collection_info:
            for output_name, output in outputs:
                self.invocation_step.add_output(output_name, output)
            self.invocation_step.job = job