    def run(self, lines):
        source = '\n'.join(lines)
        parser = HTMLExtractor(self.md)
        parser.feed(source)
        parser.close()
        return ''.join(parser.cleandoc).split('\n')