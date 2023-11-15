    def __hash__(self):
        return hash(self.get('original_title', '') + self.get('original_url', ''))