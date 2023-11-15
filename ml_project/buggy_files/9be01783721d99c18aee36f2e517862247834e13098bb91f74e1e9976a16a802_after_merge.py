    def __eq__(self, other):
        return (self.get('original_title') == other.get('original_title') and
                self.get('original_url') == other.get('original_url'))