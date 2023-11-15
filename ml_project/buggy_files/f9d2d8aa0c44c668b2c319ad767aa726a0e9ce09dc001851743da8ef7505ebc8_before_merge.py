    def sweep(self, arguments):
        self.arguments = arguments
        returns = []
        while not self.is_done():
            batch = self.get_job_batch()
            results = self.launcher.launch(batch)
            returns.append(results)
            self.update_results(results)
        return returns