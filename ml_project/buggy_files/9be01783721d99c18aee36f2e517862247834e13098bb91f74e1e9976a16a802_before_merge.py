    def __eq__(self, other):
        return self.get('title') == other.get('title') and self.get('original_url') == other.get('original_url')