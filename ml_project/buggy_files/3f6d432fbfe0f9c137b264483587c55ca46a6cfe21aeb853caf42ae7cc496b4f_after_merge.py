    def summarize(self, title: Optional[str] = None, file=None) -> None:
        """Print a summary of the dataset."""
        print(self.summary_str(title=title), file=file)