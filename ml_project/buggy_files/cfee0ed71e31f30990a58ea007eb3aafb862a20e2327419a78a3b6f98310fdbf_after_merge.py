    def get_documentation(self, content):
        """Get documentation from inspect reply content."""
        data = content.get('data', {})
        text = data.get('text/plain', '')
        if text:
            text = re.compile(ANSI_PATTERN).sub('', text)
            signature = self.get_signature(content).split('(')[-1]
            if signature:
                documentation = text.split(signature)
                if len(documentation) > 1:
                    return documentation[-1].split('Type:')[0]
            else:
                return text.split('Docstring:')[-1].split('Type:')[0]
        else:
            return ''