    def record_success(self, execution_slice, job, outputs):
        super().record_success(execution_slice, job, outputs)
        if not self.collection_info:
            self.invocation_step.job = job