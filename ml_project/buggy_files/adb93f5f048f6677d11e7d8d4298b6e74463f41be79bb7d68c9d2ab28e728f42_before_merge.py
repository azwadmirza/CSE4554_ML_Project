    def on_received_search_completions(self, completions):
        self.received_search_completions.emit(completions)
        self.search_completion_model.setStringList(completions["completions"])