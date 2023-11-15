    def analyze(self, type: Optional[Type]) -> None:
        if type:
            analyzer = TypeAnalyserPass3(self.fail, self.options, self.is_typeshed_file)
            type.accept(analyzer)
            self.check_for_omitted_generics(type)