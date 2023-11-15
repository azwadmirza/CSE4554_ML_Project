    def __repr__(self):
        ret = super(UnifiedResponse, self).__repr__()
        ret += '\n'
        for block in self.responses:
            ret += "Results from the {}:\n".format(block.client.__class__.__name__)
            ret += repr(block)
            ret += '\n'

        return ret