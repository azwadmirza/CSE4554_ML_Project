    def _index_name(self, col):
        if col == "__index__":
            return None

        match = re.search("__index__\\d+_(.*)", col)
        if match:
            name = match.group(1)
            if name == "__None__":
                return None
            return name

        return col