    def __hash__(self):
        return hash(self.get('title', '') + self.get('original_url', ''))