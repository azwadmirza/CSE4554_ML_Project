    def dump(self, file=None):
        # Avoid early bind of sys.stdout as default value
        file = file or sys.stdout
        for offset, block in sorted(self.blocks.items()):
            print('label %s:' % (offset,), file=file)
            block.dump(file=file)