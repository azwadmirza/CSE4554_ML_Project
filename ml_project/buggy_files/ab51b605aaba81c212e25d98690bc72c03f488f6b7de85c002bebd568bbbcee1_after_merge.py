    def make_type_analyzer(self, indicator: Dict[str, bool]) -> TypeAnalyserPass3:
        return TypeAnalyserPass3(self.sem.lookup_qualified,
                                 self.sem.lookup_fully_qualified,
                                 self.fail,
                                 self.sem.note,
                                 self.sem.plugin,
                                 self.options,
                                 self.is_typeshed_file,
                                 indicator,
                                 self.patches)