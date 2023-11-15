    def detab(self, block):
        """ Remove one level of indent from a block.

        Preserve lazily indented blocks by only removing indent from indented lines.
        """
        lines = block.split('\n')
        for i, line in enumerate(lines):
            if line.startswith(' '*4):
                lines[i] = line[4:]
        return '\n'.join(lines)