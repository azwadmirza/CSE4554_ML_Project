    def _get_docstring(self):
        """Find the docstring we are currently in"""
        left = self.position
        while left:
            if self.source_code[left: left + 3] in ['"""', "'''"]:
                left += 3
                break
            left -= 1
        right = self.position
        while right < len(self.source_code):
            if self.source_code[right - 3: right] in ['"""', "'''"]:
                right -= 3
                break
            right += 1
        if left and right < len(self.source_code):
            return self.source_code[left: right]