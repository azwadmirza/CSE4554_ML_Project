    def interpret_results(self, results: Optional[CatalogResults]) -> bool:
        if results is None:
            return False
        if results.errors:
            return False
        compile_results = results._compile_results
        if compile_results is None:
            return True

        return super().interpret_results(compile_results)