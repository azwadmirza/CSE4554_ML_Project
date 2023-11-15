    def get_documentation(self, content):
        """Get documentation fron inspect reply content."""
        data = content.get('data', {})
        text = data.get('text/plain', '')
        signature = self.get_signature(content).split('(')[-1]
        if text:
            documentation = text.split(signature)
            if len(documentation) > 1:
                return documentation[-1]