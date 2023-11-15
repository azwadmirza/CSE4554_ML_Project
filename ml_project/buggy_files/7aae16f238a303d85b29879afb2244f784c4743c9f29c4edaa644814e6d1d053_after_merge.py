    def to_string(node):
        """Convert Doxygen node content to a string."""
        result = []
        if node is not None:
            for p in node.content_:
                value = p.value
                if not isinstance(value, six.text_type):
                    value = value.valueOf_
                result.append(value)
        return ' '.join(result)