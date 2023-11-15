    def interpret_results(self, results):
        if results.errors:
            return False
        compile_results = results._compile_results
        if compile_results is None:
            return True

        return super().interpret_results(compile_results)